# Plan

> S-A1 senaryosu 16 Eylül 2026 14:30'da açıldı. Bu belge olay günü uyguladığımız yaklaşımı ve adım planını özetler.

## Yaklaşım

**İlke:** Alarm tipi tek başına olay demek değildir (senaryo verisi tipleri olaylar arasında paylaşır). Olay, bir sinyalin **beklenenin üzerinde, nedensel-topolojik olarak tutarlı biçimde yoğunlaşmasıdır**. Bu yüzden plan: önce geniş profil (ölç), sonra odaklı hipotez probları (doğrula), sonra hipotezleri **elle kodlamadan** genel bir korelasyon motoruna dök (genelle), son olarak kartla ve denetle.

Kabul hedeflerimiz (senaryodan): tüm 3.000 alarm işlenir; ≤15 kart; her kartta hipotez+gerekçe+etkilenen servisler+sayı+zaman+ilk aksiyon (sahip+durum); gürültü gerekçeli elenir; canlı demo.

## Adımlar (uygulanan sıra)

| Saat | Adım | Çıktı |
|---|---|---|
| 14:30–14:35 | Paket indi; dedicated branch (`feat/sa1-alarm-storm`), venv, `data/` gitignore, sözlük+brifing okuma | `memory.md` 2026-09-16 |
| 14:35–14:40 | **Keşif profili** — dağılımlar, dakikalık histogram, burst adayları, mesaj şablonları, graf özeti | `scripts/explore_profile/profile_report.md` |
| 14:40–14:50 | **Hipotez probları** — rack yerelliği, blame hedefleri, yavaş-yanma zaman çizelgeleri → 5 olay hipotezi | `scripts/hypothesis_probe/probe_report.md` |
| 14:50–15:00 | **Çekirdek motor** — anomali hücreleri → tohum kümeleme → attach → kök neden skorlaması → gürültü denetimi; iterasyonlarla yanlış birleşimler kırıldı (3 kart → 8 → **5 doğru kart**) | `src/alarmstorm/engine.py`, commit 47cd27b |
| 15:00–15:10 | **Kartlar + dashboard + aksiyon sunucusu** — gömülü grafikli tek dosya HTML, canlı yaşam döngüsü API'si, ekran görüntüleri | `src/alarmstorm/dashboard.py`, `serve.py`, `demo/` |
| 15:10–15:25 | **Teslim** — README, AI_JURI, docs, prompts, submission.json, `pip freeze` | repo kökü |

## Sapmalar ve dersler

- İlk motor koşusu 3 kart verdi: rack olayı + üç ayrı olay tek kartta birleşmişti (senaryonun "yanlış birleştirme" tuzağı). Rack bağlantısını yalnızca ağ alarmlarına, sürdürülen kaynak sinyallerini yalnızca kendi bağımlılık yönüne bağlayarak kırıldı — commit geçmişinde adım adım görülür.
- "Kar topu" pencere büyütme, hub servisin (session-service) olay yutmasına yol açtı; güçlü kanıtla (blame/anomali) frenlendi.
