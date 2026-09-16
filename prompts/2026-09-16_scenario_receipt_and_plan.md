# İstem Kaydı — 01: Senaryo alımı ve anında plan

- **Zaman:** 2026-09-16 14:30 (senaryo açılışı)
- **Kaynak:** İnsan (kaptan) — senaryo metnini yapıştırdı: "senaryo yukarıdaki gibi geldi" (S-A1 Alarm Fırtınası brifingi tam metni)
- **Model:** ZCode / GLM-5.3 (agent)

## İstem (özü)

İnsan, S-A1 senaryo brifinginin tam metnini sağladı ve beklenen tepki, daha önce `memory.md`'ye kaydedilmiş olay günü planıydı: "the moment the data package is released, work on the provided large data file starts IMMEDIATELY — first action is opening a dedicated branch, then starting directly on the file."

## Agentın yanıtı / yürütülen iş

1. `memory.md` + `CONVENTIONS.md` okundu (protokol gereği), git durumu doğrulandı.
2. Dedicated branch `feat/sa1-alarm-storm` açıldı; `data/` `.gitignore`'a eklendi (veri paketi asla repoya girmez); Python 3.12 venv kuruldu.
3. Paket (lifebox zip) açıldı; `VERI_SOZLUGU.md` ve `SENARYO_BRIFINGI.md` kod yazmadan önce okundu (senaryonun zorunlu tuttuğu sıra).
4. Senaryo kuralları `memory.md`'ye bağlayıcı olgular olarak kaydedildi (değerlendirme ölçütleri, 17:30 sert sınırı, yanlış-birleştirme tuzağı vb.).

## Karar

Keşif→hipotez→genel motor→kart→dashboard sırası uygulandı (bkz. `docs/plan.md`). İnsan, beş olay hipotezinin sohbetteki sunumunu gördü ve onayladı.
