# İstem Kaydı — 03: Genel korelasyon motoru ve iteratif düzeltmeler

- **Zaman:** 2026-09-16 14:50–15:05
- **Model:** ZCode / GLM-5.3 (agent, kendi yürütüşü; her koşu `--debug` ile)

## Görev istemi

"Hipotezleri elle kodlama. Şunu üret: (1) tip-bazlı taban çizgisine göre anomali hücresi damgalama; (2) union-find ile tohum kümeleme — aynı servis / blame kenarı / ≤1-hop bağımlılık / yalnız ağ alarmlarında rack yerelliği; (3) her alarmı nedensel olarak en yakın olaya bağlayan (blame > servis > graf mesafesi, eşitlikte sıcaklık) frenli kar-topu attach; (4) kök neden skorlaması — blame, kök-tipli marker ağırlığı, grafın açıklama gücü, erkenlik, kritiklik + DB katmanı indirimi + rack terfisi; (5) gerekçeli gürültü denetimi. Tüm eşikler CLI argümanı olsun."

## İterasyon geçmişi (hata → tanı → düzeltme; commit geçmişinde izlenebilir)

| # | Belirti | Kök neden | Düzeltme |
|---|---|---|---|
| 1 | 3 kart; billing+session+ppgw tek kartta | rack bağlantı kuralı network olmayan markerları da birleştiriyordu | rack bağı yalnızca ağ alarmlarına |
| 2 | Toplu iş olayının kökü yanlış servis | `db_conn_pool` tohum olamıyordu | marker setine eklendi |
| 3 | billing-db, kendi servisine yeniliyordu | türev semptomlar (conn_pool) kök ağırlığında sayılıyordu | kök-tipli ağırlıklar + katman indirimi + "tablespace" katman blame'i |
| 4 | 2.068 alarmlık dev kart | hub servis (session) topoloji köprüsüyle fırtınayı yuttu; pencere büyütme tüm pass sonunda | sürdürülen sinyal yalnız kendi bağımlılık yönüne; pencere büyütme anında ama yalnız güçlü kanıtla |
| 5 | 8 kart (billing ve subscriber aileleri bölünmüş) | komşu dilim + dist-1 bağı yoktu; attach kar topu yavaş | dist-1 gap-1 izni; anında pencere büyütme |
| 6 | Süreklilik sinyalleri yan olayları köprüledi | sus kuralı yönü yanlıştı (bağımlılar da bağlanabiliyordu) | yalnız "kendisinin bağımlı olduğu" servise bağlanır |

## Sonuç

3.000 alarm → **5 kart, beş kök neden de doğru**: session-service sızıntısı (yavaş gelişen, 611), dc1/rack-A ağ kesintisi (718), billing-db disk/tablespace (400), payment-provider-gw dış sağlayıcı (245), subscriber-db havuz (407). Gürültü 619, gerekçeli.

## İnsan rolü

Kartlar ve kökler sohbette sunuldu; insan "5 olay hipotezinin motor tarafından bağımsız olarak yeniden üretilmiş olması"nın sunumda vurgulanmasını istedi (AI_JURI.md §1-2'ye işlendi).
