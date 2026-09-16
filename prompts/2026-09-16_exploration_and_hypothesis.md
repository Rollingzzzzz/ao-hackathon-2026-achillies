# İstem Kaydı — 02: Keşif profili ve hipotez üretimi

- **Zaman:** 2026-09-16 14:35–14:50
- **Model:** ZCode / GLM-5.3 (agent, kendi yürütüşü — insanın kayıtlı talimatı: "geliştirme anında kendi kendine deniyorsa mutlaka --debug ile dener")

## Görev istemi (agentın kendi task tanımı, insanın kurumsal sözleşmesinden türetilen)

"Veri paketinin tamamını tek geçişte profil et: dağılımlar, dakikalık zaman histogramı, burst adayları, mesaj şablonları (değişken token'ları placeholder'a çevirerek), bağımlılık grafiği özeti, host envanteri çapraz kontrolleri, rack/dc yerelliği. Ardından profildeki şüpheleri odaklı problarla doğrula: infra hata tiplerinin servis-zaman dağılımı, ağ alarmlarının rack yerelliği, timeout/conn_refused mesajlarından suçlanan hedef servisin ayrıştırılması (blame), yavaş gelişen olay adaylarının zaman çizelgeleri."

## Üretilen çıktılar

- `scripts/explore_profile/explore_profile.py` + `profile_report.md` (ilk koşu 0.1 sn)
- `scripts/hypothesis_probe/hypothesis_probe.py` + `probe_report.md`

## Kritik bulgular (hipotezlerin temeli)

1. **Blame madeni:** `timeout/conn_refused/ext_*` mesajları başarısız çağrılan servisi İSİMLE yazıyor → bedava nedensellik kenarları.
2. dc1/rack-A'da 01:40–01:50 arası 62 ağ alarmı (diğer rackler ≤5) → rack olayı + bağımlılık çağlanı.
3. billing-db `disk_full` 17× (hepsi sev5, "%100 dolu", 02:05–02:09) → `db_write_fail` zinciri billing-service/invoice-batch'e.
4. session-service `mem_high` pencere başından sürekli → `gc_pressure` 02:11 → `oom_risk` 02:38 → 02:30–03:03 arası 40 kez timeout ile suçlanıyor (yavaş gelişen olay).
5. payment-provider-gw: tüm `ext_slow/ext_unreach` tek sağlayıcıyı işaret ediyor, 79 kez suçlanıyor (02:41–03:00) — session olayıyla ZAMAN İÇİNDE ÇAKIŞIYOR (yanlış birleştirme tuzağı burada).
6. subscriber-db `db_conn_pool` 03:00 sonrası + batch_slow/batch_overlap.

## İnsan rolü

Bulgular sohbette Türkçe özet tablo ile sunuldu; insan (domain gözü) yapıyı onayladı, motorun bu hipotezleri ELLE KODLAMADAN, genel kurallarla yeniden üretmesi kararlaştırıldı.
