# İstem Kaydı — 04: XAI kart metinleri, dashboard, canlı aksiyon takibi

- **Zaman:** 2026-09-16 15:00–15:20
- **Model:** ZCode / GLM-5.3 (agent)

## Görev istemi

"Her olay kartı sunuma hazır olmalı: Türkçe doğal dil kök neden hipotezi (insan sunacak), ölçülmüş sayılarla kanıt maddeleri, KARŞI OLASILIKLAR ve neden elendikleri, etkilenen servisler (sayılarla), önerilen ilk aksiyon + sahip + durum. Dashboard tek dosya HTML olsun (veri+grafik gömülü, çevrimdışı açılabilsin), koyu NOC teması. Aksiyon yaşam döngüsü (açık→işlemde→kapalı) demoda CANLI değişmeli ve kalıcı olmalı — dış bağımlılık olmadan (stdlib http.server). Görsel doğrulama tarayıcı otomasyonuyla yap, ekran görüntülerini demo/'ya koy."

## Yürütülen iş

- `src/alarmstorm/cards.py` — kök-türüne göre hipotez/aksiyon şablonları; kanıt maddeleri motorun ölçtüğü sayılardan üretilir (sabit sayı YOK; her kart veriden hesaplanır).
- `src/alarmstorm/dashboard.py` — 574 KB tek dosya; kartlar, gürültü denetim tablosu, grafikler gömülü.
- `serve.py` — `GET/POST /api/actions`; durum geçmişi `out/actions.json`'a atomik yazılır; ASCII takma adlar (acik/islemde/kapali) konsol/demoda kodlama sorununa karşı kabul edilir.
- Hata ayıklama kayda değer: dashboard JS'i hiç çalışmadı → sayfa içi sözdizim bisection'ı ile `str.replace` hedefinin anahtarı da yuttuğu bulundu (`"per_type": {}` → yalnız değerle değiştirilmiş); tek yerde düzgün gömmeyle giderildi.
- Doğrulama: DOM tabanlı (5 kart, 5 çip, 7/7 görsel, taşma yok, durumlar kalıcı) + tarayıcı içi canlı düğme tıklaması (EVT-01 → İŞLEMDE, geçmiş kaydı oluştu) + `demo/dashboard_{top,full}.png`.

## İnsan rolü

Demo akışı kararı: sunumda önce `python run.py --debug` (canlı üretim), sonra `python serve.py` + dashboard, aksiyon düğmesi sahnesi, en son gürültü denetimi görünümü.
