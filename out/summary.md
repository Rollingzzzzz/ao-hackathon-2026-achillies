# AlarmStorm — Özet Rapor

- Toplam alarm: **3000** → olay kartı: **5** (indirgeme oranı 1:600)
- Olaylara bağlanan alarm: **2381** · gürültü olarak elenen: **619**

| Kart | Kök neden | Örüntü | Aralık | Alarm | Kritik | Aksiyon sahibi | Durum |
|---|---|---|---|---|---|---|---|
| EVT-01 | Bellek tükenmesi (yavaş gelişen) — session-service | yavaş gelişen | 01:31:33–02:56:51 | 611 | 🔴 | Oturum Servisi Sahibi | açık |
| EVT-02 | Ağ kesintisi — dc1/rack-A (rack üzeri ağ altyapısı) | ani patlama | 01:38:32–02:00:43 | 718 | 🔴 | Ağ Operasyon (NOC) | açık |
| EVT-03 | Disk / tablespace doluluğu — billing-db | ani patlama | 02:01:38–02:31:11 | 400 | 🔴 | DBA Ekibi | açık |
| EVT-04 | Dış sağlayıcı degradasyonu — payment-provider-gw | ani patlama | 02:37:03–03:03:31 | 245 | 🔴 | Ödeme Platformu Nöbetçisi | açık |
| EVT-05 | Bağlantı havuzu tükenmesi — subscriber-db | ani patlama | 03:02:08–03:30:20 | 407 | 🟠 | Veritabanı Operasyonu | açık |

## Gürültü denetimi

| Eleme gerekçesi | Alarm sayısı |
|---|---|
| below_anomaly_threshold | 596 |
| no_topology_link | 59 |
| outcompeted | 22 |
