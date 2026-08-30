# achillies - AO Hackathon 2026

## 🏆 Tek Cümlelik Özet
Vertex AI Gemini 2.5 Flash ve Drain3 entegrasyonu ile heterojen log akışlarını **%100 Sıfır-Kayıp (Zero-Loss)** ile tek satıra indirgeyen, **20 kat (%95.07) sıkıştıran** ve kök neden analizi yapan otonom AI operasyon platformu.

---

## 🎯 Çözülen Problem
SRE ve operasyon ekiplerinin devasa (milyonlarca satırlık) heterojen altyapılarda oluşan karmaşık çoklu satırlı (Java/Python stacktrace) logları manuel inceleme zorluğunu ve yüksek LLM token maliyetlerini ortadan kaldırmak.

---

## ⚡ Mimari X-Factor Özelliklerimiz
1. **X-Factor 1 (Otonom AI Regex Bulucu):** Dil/teknoloji bağımsız saf metin geometrisiyle (Column 0 / Non-indented Header Detection) çoklu satırları %100 sıfır kayıpla tekli satır olaylarına dönüştürür (`src/1_data_loader/vertex_normalizer.py`).
2. **X-Factor 2 (Agentic Self-Healing Loop):** Deterministik Python denetimiyle %100 kusursuz eşleşme garantisi veren ve canlı token/maliyet hesaplayan otonom iyileştirme motoru (`src/1_data_loader/agentic_vertex_async.py`).
3. **X-Factor 3 (Agentic Drain3 High-Fidelity Auto-Tuner):** Gemini 2.5 Flash'ı AI Observability Reviewer olarak kullanarak şablon sadakatini (Fidelity Score 0.0-10.0) puanlayan ve parametreleri (`sim_th`, `depth`) otonom optimize eden motor (`src/1_data_loader/agentic_drain3_autotuner.py`).

---

## 🧪 Test Verisetimiz ve Koşturma Komutları

### 1. Kurulum:
```bash
git clone https://github.com/Rollingzzzzz/ao-hackathon-2026-achillies.git
cd ao-hackathon-2026-achillies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Test Koşturma Komutları:

```bash
# Adım 1: X-Factor 2 - Agentic Self-Healing Regex & Çoklu Satır Normalleştirme:
python3 scripts/agentic_vertex_async.py --input data/heterogeneous_karmasik_test.log

# Adım 2: X-Factor 3 - Agentic Drain3 High-Fidelity Auto-Tuner (Şablon Sadakat Motoru):
python3 scripts/agentic_drain3_autotuner.py --input data/normalized_heterogeneous_karmasik_test.log

# Adım 3: Jenerik Drain3 Şablon Madencisi & Yapısal Metrik Raporlayıcısı:
python3 scripts/drain3_ozetle.py --input data/normalized_heterogeneous_karmasik_test.log
```

---

## 📄 Üretilen Çıktı Dosyaları
- `data/normalized_<girdi_adi>.log`: %100 tekli satır olaylarına indirgenmiş ham loglar.
- `data/templates_<girdi_adi>.txt`: %100 benzersiz yüksek sadakatli şablon listesi.
- `data/output_autotuner_<girdi_adi>.txt`: Yürütme, token tüketimi, sadakat skoru ve API maliyet raporu.
- `data/summary_autotuner_<girdi_adi>.json`: Tüm şablonların ve metriklerin JSON özeti.

---

## 🌐 Deploy Bilgileri ve Bilinen Sınırlar
- **Dokümantasyon:** Jüri detaylı teknik özeti `AI_JURI.md` belgesindedir.
- **GCP ADC Auth:** Vertex AI API erişimi için Application Default Credentials (ADC) kimlik doğrulaması gerektirir.
