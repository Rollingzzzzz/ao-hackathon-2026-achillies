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

## 2. Tur — Öz-denetim geçişi (16:30–17:15, kullanıcı kararı: "bir yerlerde bize gol atılmış olabilir")

Kullanıcı senaryo yazarından ("Selahattin abi") gelmiş olabilecek bilinçli bir tuzağa karşı belirleyici bir denetim istedi. Ajan `scripts/trap_audit/` iç denetim aracını kurdu (proxy yalnız denetimde; motor ve teslim dokümanları alarm_id'yi kullanmaz):

| # | Bulgular | Kök neden | Düzeltme |
|---|---|---|---|
| A | Eski çalışma 1.762 uniform gürültü alarmının 1.157'sini kartlara emmişti (EVT-01 %65, EVT-05 %67 gürültü) | "aynı servis"/"graf yakınlığı" puanı her severity'de bağlanıyordu; geniş olay pencereleri gürültüyü yutuyordu | attach'e çekirdek-kanıt kapısı: blame hedefi, anomali, sert hata işareti veya sev≥4 olmayan alarm kartlara giremez (`not_core_evidence` gerekçesiyle elenir) |
| B | 14 gerçek kaskad kuyruğu alarmı gürültü sanıldı (02:57–03:03 auth/web-bff/mobile-bff; dahil tek sev5 ALM-01048) | pencere 2 süpürmede geç büyüyor, timestamp-sıralı geçiş kuyruklara yeniden teklif yapamıyordu | süpürme 2→3; güçlü alarmlar komşu servislerde de çekirdek kanıt sayılır |
| C | EVT-01/04 karşı-olasılıkları boş (tek servisli tohum) | aday havuzunda root'tan başka servis yoktu | etkilenen servislerden ölçümlü dolgu adayları |
| D | EVT-05 kök yönü şüphesi | — | KANIT: subscriber-db sinyalleri 03:03:50'de, batch_overlap 03:05:28'de → kök subscriber-db doğru, değişiklik yok |

**Sonuç (2. tur):** 5 kart ve kökler değişmedi; bağlı alarm 2.381→1.301 (1.124 olay bandı), gürültü 1.699 gerekçeli; iç proxy'ye göre gürültü eleme %34.3→%92.2, tüm 248 sev5 kartlarda; kalan 74 elenen gerçek dahil tümü sev3 tekil zayıf sinyal (54'ü blame'siz latency_high).
