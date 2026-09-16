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
- Kabul: **5 olay kartı** (≤15), her kartta zorunlu tüm alanlar; 619 alarm gerekçeli gürültü (bu sayı Faz 6'da 1.699'e yükseldi).

## Faz 4 — Ürünleştirme (15:05–15:15)
- Olay kartları metinleri (XAI), PNG grafikler, tek dosya dashboard, aksiyon yaşam döngüsü sunucusu; görsel doğrulama + `demo/` ekran görüntüleri.
- Kabul: `python run.py` sıfırdan ayağa kalkıp sonuç üretiyor; aksiyon açık→işlemde→kapalı canlı değişiyor ve kalıcı.

## Faz 5 — Teslim (hedef aralığın çok üzerinde erkenden)
- README (kurulum+kullanım+kütüphane beyanı), AI_JURI.md (kanıtlı), docs/ üçlüsü, `prompts/`, `submission.json`, `pip freeze > requirements.txt`.
- Kabul: son kontrol listesi tam; son commit 17:30 sert sınırından çok önce atılmış.

## Faz 6 — Öz-denetim geçişi (16:30–17:15, kullanıcı kararı)
- Şüphe: "senaryo yazarı çözümü yanlış yöne çekebilecek bir tuzak kurmuş olabilir." İç denetim aracı `scripts/trap_audit/` kuruldu (yalnız denetimde kullanılan mekanik proxy; motor ve teslim dokümanları alarm_id'yi asla kullanmaz).
- Bulgular: eski çalışma 1.762 uniform gürültü alarmının 1.157'sini kartlara emmişti (%35 gürültü eleme recall); 14 gerçek kaskad kuyruğu alarmı (dahil tek sev5 ALM-01048) gürültü sanılmıştı; EVT-05 kök yönü doğrulandı (subscriber-db sinyalleri batch_overlap'ten önce).
- Düzeltme: attach'e çekirdek-kanıt kapısı (blame / anomali / sert hata işareti / sev≥4) + 3 süpürme + ölçümlü karşı-olasılık dolgusu. Sonuç: gürültü eleme %34.3→%92.2, tüm 248 sev5 kartlarda, 5 kart ve kökler değişmedi.
- Kabul: teslim dokümanları (README/AI_JURI/submission.json/docs) yeni ölçülmüş rakamlarla tutarlı; `demo/` görüntüleri yeni dashboard'dan.
