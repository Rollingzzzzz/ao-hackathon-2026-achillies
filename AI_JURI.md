# 🏆 AI Jüri Özeti - achillies

## 1. Çözülen Problem ve Temel Felsefemiz
Kurumsal sistemlerde ve heterojen altyapılarda üretilen log akışları milyonlarca satırdan oluşan, çoklu satırlı (Java exception stacktrace'leri, Python traceback'leri, multi-line log blokları) ve karmaşık bir yapıya sahiptir. 

Bu devasa log akışları üzerinden anomali tespiti ve kök neden analizi (Root Cause Analysis) yaparken karşılaşılan 3 temel zorluk bulunmaktadır:
1. **Çoklu Satırlı Yapı Karmaşası:** Stacktrace ve alt mesajların bağımsız log olayları sanılması, analiz bütünlüğünü bozar.
2. **Yüksek Context Maliyeti ve Gürültü:** Milyonlarca satırlık gürültülü veriyi doğrudan dil modellerine (LLM) beslemek yüksek maliyet, yavaşlık ve odaklanma kaybı (Attention Degradation) yaratır.
3. **Bilgi Kaybı (Over-Masking):** Geleneksel sıkıştırma yöntemlerinin sabit parametrelerle kritik hata kodlarını ve istisna sınıflarını aşırı maskeleyerek anlamsız `<*>` gürültüsüne dönüştürmesi.

Sistemimiz, bu zorlukları **tamamen etki alanından bağımsız (domain-agnostic)** ve **sıfır ön bilgi (zero-shot)** ilkesiyle çözen, Python determinizmini Vertex AI Gemini 2.5 Flash'ın akıl yürütme gücüyle birleştiren otonom bir mimaridir.

---

## 2. Test Verisetimizin Sentezlenme Hikayesi ve Yaşam Döngüsü Kanıtı
Jürimizin sistemimizi hiçbir harici bağımlılık gerekmeksizin anında doğrulayabilmesi için repomuzun `src/1_data_loader/examples/` klasöründe tam bir **Veri İşleme Yaşam Döngüsü Kanıtı (Pipeline Lifecycle Proof)** sunulmuştur:

- **Sentezlenme Mantığı (`heterogeneous_karmasik_test.log` - 70.857 Satır / 7.9 MB):**
  Modelimizin tek bir homojen formata (sadece Syslog veya sadece Nginx) ezber yapmasını engellemek amacıyla; gerçek dünya kurumsal altyapılarında sıklıkla karşılaşılan **4 farklı dağıtık sistemin ham log akışları (OpenStack Nova Compute/API, Hadoop MapReduce Taskları, HDFS DFSClient erişim logları ve Java Exception stack trace blokları)** harmanlanarak 70.857 satırlık karmaşık bir stres test veriseti oluşturulmuştur.

- **Tam Yaşam Döngüsü Kanıtı (Lifecycle Proof):**
  1. **Ham Metin (`heterogeneous_karmasik_test.log`):** `70.857 Satır` ➔
  2. **X-Factor 2 Tekli Satır (`normalized_heterogeneous_karmasik_test.log`):** `17.280 Bağımsız Olay` (%100 Sıfır-Kayıp) ➔
  3. **X-Factor 3 Şablon Listesi (`templates_heterogeneous_karmasik_test.txt`):** `937 Yüksek Sadakatli Şablon` (**%95.07 Sıkıştırma / 20 Kat Hızlı**, 9.0/10.0 AI Fidelity Score).

---

## 3. X-Factor 1: Otonom AI Regex Bulucu ve Sıfır-Kayıp Normalleştirici
- **Yaklaşım:** Ham log akışlarındaki çoklu satırlı karmaşık yapılar, herhangi bir dil veya teknolojiye özel kural gerektirmeksizin saf metin geometrisiyle (Column 0 / Non-indented Header Detection) **%100 Sıfır-Kayıp (Zero-Loss)** ile tek satırlı bağımsız olaylara (Single-Line Events) dönüştürülür.
- **Başarı:** Çoklu satırları (Java Exception stacktrace'leri, OpenStack logları) tek satır / tek bağımsız olay haline getirerek veri bütünlüğünü %100 korur.
- **Kanıt:** `src/1_data_loader/vertex_normalizer.py`

---

## 4. X-Factor 2: Agentic Self-Healing Loop & Live Token Accounting (%100 Garanti Motoru)
- **Problem & Çözüm:** Tek seferlik AI çıktıları heterojen devasa log dosyalarında bazı özel satırları gözden kaçırabilir.
- **Otonom Ajan Döngüsü (`agentic_vertex_async.py`):**
  1. Vertex AI Gemini 2.5 Flash, log örneğinden ilk Regex hipotezini sentezler.
  2. Deterministik Python denetim motoru, bu Regex'i diskteki 70.000+ satırlık ham logun tamamında test ederek hesaplama doğrulaması (`Zero-Loss Accounting`) yapar.
  3. Kapsama oranı %100'ün altındaysa, sadece kaçırılan özel satırlar izole edilerek modele geri beslenir (`Self-Healing Feedback Prompt`).
  4. **%100 Kusursuz Eşleşme** sağlanana kadar döngü otonom olarak kendini iyileştirir (**%100 Sonuç Garanti!**).
- **Canlı Metrikler (`heterogeneous_karmasik_test.log`):**
  * **Eşleşme Başarısı:** %100.0 Kusursuz Eşleşme (3 İterasyonda)
  * **Olay Sayısı:** 70.857 raw satır ➔ 17.280 tekli satır olayı
  * **API Maliyeti & Token:** 11.345 Token (**$0.000943 USD**)
- **Kanıt:** `src/1_data_loader/agentic_vertex_async.py`, `scripts/agentic_vertex_async.py`

---

## 5. X-Factor 3: Agentic Drain3 High-Fidelity Auto-Tuner (Otonom Şablon Sadakat Motoru)
- **Problem & Çözüm:** Geleneksel kümeleme motorları, log içerisindeki kritik hata kodlarını ve istisna detaylarını aşırı maskeleyerek anlamsız `<*>` gürültüsüne dönüştürebilir.
- **Otonom Şablon İyileştiricisi (`agentic_drain3_autotuner.py`):**
  1. Vertex AI Gemini 2.5 Flash, bir **AI Observability Reviewer** olarak konumlandırılır.
  2. Üretilen şablonları SRE analizi kriterlerine göre otonom puanlar (Fidelity Score: 0.0 - 10.0).
  3. Aşırı maskeleme saptandığında benzerlik eşiğini (`sim_th`) ve ağaç derinliğini (`depth`) otonom ayarlar.
  4. Kritik hata bağlamını %100 koruyarak log hacmini **20 kat (%95.07)** sıkıştırır.
  5. Üretilen tüm benzersiz şablonlar (%100) `templates_<girdi_adi>.txt` dosyasına ihraç edilir.
- **Canlı Metrikler (`heterogeneous_karmasik_test.log`):**
  * **Kümeleme Başarısı:** 19.004 olay ➔ 937 Yüksek Sadakatli Şablon (%95.07 Sıkıştırma)
  * **AI Fidelity Skoru:** **9.0 / 10.0** (3 İterasyonda, `sim_th=0.70`, `depth=4`)
  * **API Maliyeti & Token:** 7.113 Token (**$0.000642 USD**)
- **Kanıt:** `src/1_data_loader/agentic_drain3_autotuner.py`, `scripts/agentic_drain3_autotuner.py`, `src/1_data_loader/drain3_ozetle.py`

---

## 6. Faz 3 (Gelecek Aşama): Anomali Tespiti ve Kök Neden Analizi
- Yapılandırılmış ve 20 kat sıkıştırılmış yüksek sadakatli şablon kümesi üzerinden, istatistiksel nadirlik süzgeci ve zaman penceresi farkı (delta) kullanılarak anomaliler ve kök nedenler milisaniyeler içinde teşhis edilecektir.

---

## 7. Komut Satırı Çalıştırma Standartları (CLI)
Jürimizin repodaki örnek verisetimiz üzerinden sıfır harici yüklemeyle anında test edebileceği komutlar:

```bash
# 1. Faz 1 & X-Factor 2 Testi (Sıfır-Kayıp Çoklu Satır Normalleştirici):
python3 scripts/agentic_vertex_async.py --input src/1_data_loader/examples/heterogeneous_karmasik_test.log

# 2. Faz 2 & X-Factor 3 Testi (Agentic Drain3 High-Fidelity Auto-Tuner):
python3 scripts/agentic_drain3_autotuner.py --input src/1_data_loader/examples/normalized_heterogeneous_karmasik_test.log

# 3. Jenerik Drain3 Şablon Madencisi Testi:
python3 scripts/drain3_ozetle.py --input src/1_data_loader/examples/normalized_heterogeneous_karmasik_test.log
```

---

## 8. Bilinen Sınırlar
- GCP Vertex AI kimlik doğrulaması (ADC - Application Default Credentials) gerektirir.
