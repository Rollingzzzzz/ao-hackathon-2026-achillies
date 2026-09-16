# Mimari

AlarmStorm tek makinede çalışan, deterministik bir boru hattı ve iki yüzeyden oluşur: **üretime** (`run.py`) ve **sunuma** (`serve.py`).

```
data/package/katilimci_paketi/          (gitignore'lı — repoya girmez)
  alarms.csv · service_dependencies.csv · host_inventory.csv
        │
        ▼
run.py ─► src/alarmstorm/
        io.py        yükleme + blame ayrıştırma (timeout/conn_refused/ext_* hedefi)
        graph.py     bağımlılık grafiği (yönlü nedensellik + yönsüz mesafe)
        engine.py    1) anomali hücreleri  2) tohum kümeleme (union-find)
                     3) attach (frenli kar topu)  4) kök neden skorlaması
                     5) gürültü denetimi (gerekçeli eleme)
        cards.py     olay kartları: doğal dil hipotezi + kanıt + karşı
                     olasılık + aksiyon (sahip/durum) — Türkçe XAI katmanı
        report.py    markdown özet + PNG zaman çizelgeleri
        dashboard.py tek dosya HTML konsol (veri+grafik gömülü)
        cli.py       orkestrasyon + tüm eşikler CLI argümanı
        │
        ▼
out/  cards.json · events_full.json · noise_audit.json · actions.json
      charts/*.png · dashboard.html · summary.md          (kanıt amaçlı commit'lenir)
        │
        ▼
serve.py (stdlib http.server)
  GET  /            dashboard.html
  GET  /api/actions aksiyon durumları
  POST /api/actions {"id","status"} → out/actions.json (atomik yazma, kalıcı)
```

## Tasarım kararları ve gerekçeleri

- **Anomali hücresi = olayın atomu.** `(servis, tip, 5dk)` sayısı `max(3, 8×tipin global tabanı)` üstünde ise yapısal sinyal. Tip bazlı eşik, seyrek tiplerin (disk_full gibi) tek başına patlamasını da yakalar.
- **Blame kenarları.** `timeout`/`conn_refused`/`ext_*` mesajları başarısız çağrılan tarafı isimlendirir; motor bunu yönlü kenar olarak kullanır (kök skorlamada en güçlü sinyallerden). Mesaj formatı örnek veriden çıkarıldı.
- **Kümeleme frenleri (yanlış birleştirmeye karşı):** graf bağlantıları yalnız aynı 5 dk diliminde; sürdürülen kaynak sinyalleri yalnız kendi bağımlılık yönünde; rack yerelliği yalnız ağ alarmlarına. Bu üç fren, zaman içinde çakışan bağımsız olayların (sızıntı ↔ ödeme sağlayıcı) ayrı kalmasını sağlar.
- **Frenli kar topu attach.** Zayıf (mesafe bazlı) bağlanma pencereyi büyütemez; yalnız blame/anomali eşleşmeleri büyütür. Eşitlikte "o an en sıcak olay" kazanan olur.
- **Katman indirimi.** Servis, kendi `*-db` bağımlılığı sinyal veriyorsa servisin DB-katmanı hataları (db_write_fail/conn_pool) yarı ağırlıklı sayılır — türev, kök değil. `db_write_fail` mesajları ayrıca katman blame'i olarak DB'ye atfedilir ("tablespace").
- **Rack terfisi.** Ağ işaretçilerinin ≥%60'ı tek rack'te ve ≥8 adetse kök servis değil **rack** olur ("top-of-rack ağ"); kart aksiyonu NOC'a gider.
- **Denetlenebilirlik.** Her alarm ya bir kartın `alarm_ids` listesindedir ya `noise_audit.json`'da gerekçesiyle durur; `events_full.json` kök skorlarını ve tohum kimliklerini saklar. Hiçbir alarm açıklamasız kaybolmaz.
- **Atomik yazma + determinizm** tüm çıktılarda; `--debug` her aşamada ilerleme/gerekçe basar (`out/run_debug.log`).
