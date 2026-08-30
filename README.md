# achillies - AO Hackathon 2026

## Tek Cümlelik Özet
AI orkestrasyonu ile SRE olaylarında kök neden analizi ve otomatik aksiyon üreten akıllı operasyon platformu.

## Çözdüğünüz Problem
SRE ve operasyon ekiplerinin karmaşık dağıtık sistemlerde oluşan arıza ve log paketlerini manuel incelemedeki zaman kaybını ortadan kaldırmak.

## Çözümümüzün Nasıl Çalıştığı
SAKA ve AI modelleri entegrasyonu ile gelen log, metrik ve olay verilerini işler; açıklanabilir yapay zeka (XAI) destekli kök neden analizi ve otomatik remediate senaryoları sunar.

## Kurulum Adımları
```bash
git clone https://github.com/Rollingzzzzz/ao-hackathon-2026-achillies.git
cd ao-hackathon-2026-achillies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Çalıştırma Komutu
```bash
python3 src/main.py
```

## Kullanılan Tüm AI Araçları ve Model Sürümleri
- **Platform:** SAKA AI Platform
- **Modeller:** SAKA LLM Endpoints (GPT-4o / Claude 3.5 Sonnet / Llama 3)
- **Yardımcı Araçlar:** Hermes Agent CLI

## MCP Sunucu Listesi
- Henüz entegre edilen özel bir MCP sunucusu bulunmamaktadır (Etkinlik günü eklenecektir).

## Entegre Edilen API'ler
- SAKA Multi-LLM API Gateway

## Ekran Görüntüleri
*(Etkinlik günü eklenecektir - demo/ klasörü altında)*

## Deploy URL ve Bilinen Sınırlar
- **Deploy URL:** Yerel çalışma ortamı (Local execution)
- **Bilinen Sınırlar:** Sentetik veri paketleri üzerinde optimize edilmiştir.
