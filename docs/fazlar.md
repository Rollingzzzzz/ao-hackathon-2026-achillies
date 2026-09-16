# Fazlar

Olay gününde uygulanan fazlar, kabul kriterleriyle.

## Faz 0 — Hazırlık (günler öncesinden)
- Repo iskeleti, `CONVENTIONS.md` (doğrulama döngüsü, branch, gizli veri), `memory.md` karar günlüğü, AI beyan altyapısı.
- Kabul: jüri gereken tüm dosyalar mevcut; repo public.

## Faz 1 — Keşif (14:30–14:40)
- Dedicated branch + venv + `data/` gitignore; sözlük/brifing okuma; geniş profil scripti.
- Kabul: dağılımlar + histogram + burst adayları belgelenmiş (`scripts/explore_profile/`).

## Faz 2 — Hipotez (14:40–14:50)
- Odaklı probalar: rack yerelliği, blame hedefleri, yavaş-yanma çizelgeleri.
- Kabul: 5 olay hipotezi veriyle doğrulanmış (`scripts/hypothesis_probe/`).

## Faz 3 — Çekirdek motor (14:50–15:05)
- Anomali hücreleri → tohum → attach → kök skorlama → gürültü denetimi.
- Ara kabul: 3.000 alarm tam işlenir; küme sayısı stabil; yanlış birleşimler düzeltilmiş (iterasyon geçmişi commit'lerde).
- Kabul: **5 olay kartı** (≤15), her kartta zorunlu tüm alanlar; 619 alarm gerekçeli gürültü.

## Faz 4 — Ürünleştirme (15:05–15:15)
- Olay kartları metinleri (XAI), PNG grafikler, tek dosya dashboard, aksiyon yaşam döngüsü sunucusu; görsel doğrulama + `demo/` ekran görüntüleri.
- Kabul: `python run.py` sıfırdan ayağa kalkıp sonuç üretiyor; aksiyon açık→işlemde→kapalı canlı değişiyor ve kalıcı.

## Faz 5 — Teslim (hedef aralığın çok üzerinde erkenden)
- README (kurulum+kullanım+kütüphane beyanı), AI_JURI.md (kanıtlı), docs/ üçlüsü, `prompts/`, `submission.json`, `pip freeze > requirements.txt`.
- Kabul: son kontrol listesi tam; son commit 17:30 sert sınırından çok önce atılmış.
