# AI Jüri Özeti — achillies / AlarmStorm

> S-A1 "Alarm Fırtınası" · 16 Eylül 2026. Bu belgedeki her iddia bir dosya yoluyla kanıtlıdır; kanıtsız iddia yoktur.

## 1. AI Stratejimiz ve İş Akışı

**İş bölümü ilkesi:** AI (ZCode ajanı, GLM-5.3) teknik derinliği üretti — veri keşfi, hipotez üretimi, algoritma tasarımı, kod, hata ayıklama. **İnsan** gözlemci, karar verici ve sunucu olarak her aşamada loop'ta tutuldu (kabul makamı hep insan). Çalışma sözleşmemiz günler öncesinden yazılı: `CONVENTIONS.md` (doğrulama döngüsü, branch disiplini, gizli veri yasakları); günün karar günlüğü: `memory.md` (2026-09-16 bölümü).

**Olay günü AI iş akışı (gerçek sıra):**

1. Paket iner inmez AI keşif profili üretti: `scripts/explore_profile/profile_report.md` (dağılımlar, dakikalık histogram, burst adayları, mesaj şablonları, bağımlılık grafiği özeti).
2. AI, profile dayanarak **5 olay hipotezi** kurdu ve odaklı sorgularla doğruladı: `scripts/hypothesis_probe/probe_report.md` (rack yerelliği, blame hedefleri, yavaş-yanma zaman çizelgeleri). İnsan bu bulguları sohbette gördü, onayladı.
3. Hipotezler **elle kodlanmadı**; genel korelasyon motoruna dönüştürüldü: `src/alarmstorm/engine.py`. Motor "5 olay biliyorum" ile değil, eşiği aşan yoğunlaşmaları kümeleyerek aynı 5 olaya kendi başına ulaştı — senaryonun "olay sayısı söylenmez" kuralına uygun.
4. Her yazılım parçası AI tarafından `--debug` ile kendi kendine çalıştırıldı, çıktılar `scripts/*/run_debug.log` ve `out/run_debug.log` altına kaydedildi; insanın gözlemi için tam yol komutları sohbete verildi (kurumsal doğrulama döngümüz).
5. Dashboard görsel olarak AI tarayıcı otomasyonuyla doğrulandı, ekran görüntüleri `demo/` klasörüne üretildi.

**Hangi kararı insan verdi:** senaryo yorumu ve çerçeveleme (insan + AI birlikte), aracın "sunum dili Türkçe, insan sunacak" kararı, kabul/onaylama, demo senaryosu. **Hangi kararı AI verdi:** anomali eşik formülü, kümeleme kuralları, kök neden skorlama ağırlıkları, kart metin şablonları — tümü `prompts/` altındaki istem kayıtlarında izlenebilir.

Kanıt: `prompts/`, `CONVENTIONS.md`, `memory.md`, `git log` (anlamlı commit zinciri: keşif → çekirdek → dashboard → teslim).

## 2. Problemi Nasıl Çözdük

3.000 alarm → **5 olay kartı** (kabul kriteri ≤15; "nöbetçinin bakabileceği kadar"). 1.301 alarm nedensel kanıtla olaylara bağlandı, **1.699 alarm gerekçesiyle gürültü olarak elendi** (denetim görünümü dashboardda + `out/noise_audit.json` içinde alarm bazında); kritik (sev5) alarmların tamamı kartlara bağlıdır. Her kart zorunlu alanların tamamını içeriyor: kök neden hipotezi (doğal dil), kanıt maddeleri (ölçülmüş sayılarla), karşı olasılıklar, etkilenen servis listesi, alarm sayısı, zaman aralığı, sahip + durum bilgili ilk aksiyon. Opsiyonel gereksinim olan **aksiyon yaşam döngüsü** (açık → işlemde → kapalı, geçmişiyle) canlı sunucuda çalışıyor ve sunucu yeniden başlatılsa bile kalıcı.

Teslimden önce kendi çözümümüze karşı bir de **öz-denetim geçişi** yaptık (aday jeneratör davranışına karşı mekanik testler; `scripts/trap_audit/`): geniş olay pencerelerinde "aynı servis" eşleşmesiyle arka plan gürültüsünün kartlara emildiği ortaya çıktı. Attach aşamasına **çekirdek-kanıt kapısı** eklendi: bir alarm artık yalnız nedensel kanıt taşıyorsa (blame hedefi / anomali / sert hata işareti / kritik seviye) kartlara bağlanabiliyor — kart alarm sayıları 2.381 → 1.301'e indi, gürültü eleme oranı %34'ten %92'ye çıktı, 5 kart ve kök nedenler değişmedi. Düzeltmenin kendisi de commit geçmişinde görülür.

Boru hattı beş aşaması ve tasarım gerekçeleri: `README.md` §3, ayrıntı: `docs/mimari.md`.

Kanıt: `out/cards.json`, `out/summary.md`, `demo/dashboard_full.png`, `src/alarmstorm/`.

## 3. X-Factor

**Denetlenebilir nedensellik: "blame" kenarları + karşı-olasılıklı XAI kartları.**

Sıradan bir çözüm alarm tiplerine göre gruplar; bu veri setinde tipler olaylar arasında **bilinçli olarak paylaşılıldığı** için bu yaklaşım yanlış birleştirme üretir (bizde ilk denemede tam olarak bu oldu — 3 kartlık yanlış birleşim, commit geçmişinde görülür ve düzeltildi). Bizim motor üç şeyi birleştirdi:

1. **Mesajdan nedensellik çıkarma** — `timeout/conn_refused/ext_*` mesajları hangi servisin çağrılıp başarısız olduğunu isimle yazar; motor bunu ayrıştırıp yönlü nedensellik kenarı olarak kullanır (`src/alarmstorm/io.py` `parse_blame`, `src/alarmstorm/engine.py` blame skorlaması). "payment-provider-gw 79 kez suçlandı" bir kanıt maddesidir.
2. **Yanlış birleştirmeye karşı graf mesafesi freni** — zaman içinde çakışan iki bağımsız olay (session-service sızıntısı ↔ ödeme sağlayıcı degradasyonu, 02:38–03:00) topolojik olarak 4+ hop uzakta olduğu için **ayrı kartlarda** kaldı; senaryonun bilerek kurduğu tuzahı kırdı.
3. **Karşı-olasılıklar** — her kart, elenen ikinci-üçüncü adayı ve **neden elendiğini** ölçülmüş farkla yazar (ör. "billing-service: doğrudan suçlayan 43 alarm var ama kendi DB'si (%100 dolu) hatayı açıklıyor → DB katmanı indirimi"). Jüri "neden bu sonuç?" diye sorduğunda cevap kartın üzerinde.

Ek X-Factor: **gürültü denetim görünümü** — elenen 1.699 alarmın her biri kimliğiyle ve gerekçesiyle listelenir (`out/noise_audit.json`, dashboard tablosu); "gürültü elemesi" ölçütünün doğrudan kanıtı.

Kanıt: `src/alarmstorm/io.py:44-70` (blame ayrıştırma), `src/alarmstorm/engine.py` (seed kuralları `build_seeds`, skorlama `score_roots`), `out/cards.json` (`counter_hypotheses`), `demo/dashboard_full.png`.

## 4. Çalıştırma

```bash
pip install -r requirements.txt
python run.py --debug     # boru hattı: out/ altına kartlar, grafikler, dashboard
python serve.py           # http://localhost:8787 — canlı aksiyon takibiyle konsol
```

(Windows venv: `.venv\Scripts\python.exe run.py --debug`)

## 5. Bilinen Sınırlar

- **Alarm bazlı atıf belirsizliği:** çakışan olaylarda tek alarmların hangi olaya ait olduğu kesin değil (ör. mobile-bff iki olayın da mağduru); kart ayrımı doğru, alarm atfında hata payı var.
- **Kalibrasyon:** skorlama ağırlıkları bu veri setine göre ayarlandı; başka senaryolarda CLI eşikleriyle yeniden kalibre edilmeli (tümü parametreli).
- **Doğrulama yok:** gerçek olay etiketleri jüride kapalı; kök neden isabetini ölçemedik, bu yüzden her hipotez karşı-olasılıklarıyla sunuldu (senaryonun açıkça ödüllendirdiği tutum).
- Aksiyon önerileri şablon tabanlıdır; gerçek runbook entegrasyonu kapsam dışı bırakıldı.
