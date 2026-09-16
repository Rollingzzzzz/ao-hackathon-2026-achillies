# AlarmStorm — Özet Rapor

- Toplam alarm: **3000** → olay kartı: **5** (indirgeme oranı 1:600)
- Olaylara bağlanan alarm: **1301** · gürültü olarak elenen: **1699**

| Kart | Kök neden | Örüntü | Aralık | Alarm | Kritik | Aksiyon sahibi | Durum |
|---|---|---|---|---|---|---|---|
| EVT-01 | Bellek tükenmesi (yavaş gelişen) — session-service | yavaş gelişen | 01:33:35–03:05:08 | 234 | 🔴 | Oturum Servisi Sahibi | açık |
| EVT-02 | Ağ kesintisi — dc1/rack-A (rack üzeri ağ altyapısı) | ani patlama | 01:41:40–01:55:26 | 459 | 🔴 | Ağ Operasyon (NOC) | açık |
| EVT-03 | Disk / tablespace doluluğu — billing-db | ani patlama | 02:02:30–02:28:17 | 276 | 🔴 | DBA Ekibi | açık |
| EVT-04 | Dış sağlayıcı degradasyonu — payment-provider-gw | ani patlama | 02:38:31–03:01:16 | 168 | 🔴 | Ödeme Platformu Nöbetçisi | açık |
| EVT-05 | Bağlantı havuzu tükenmesi — subscriber-db | ani patlama | 03:04:41–03:30:19 | 164 | 🟠 | Veritabanı Operasyonu | açık |

## Gürültü denetimi

| Eleme gerekçesi | Açıklama | Alarm sayısı |
|---|---|---|
| `below_anomaly_threshold` | servis×tip×zaman dilimi bazında anomali eşiğini geçmeyen arka plan | 1675 |
| `no_topology_link` | pencereyle örtüşen ama bağımlılık topolojisinde olaya bağlanamayan | 95 |
| `not_core_evidence` | pencere içinde ve topolojik olarak yakın, ancak nedensel kanıt (blame hedefi, anomali, sert hata işareti veya kritik seviye) taşımayan — kasıtlı bağlama politikası gereği elendi | 19 |
| `no_time_overlap` | hiçbir olay penceresine denk gelmeyen | 18 |
