# LIBROTRACK
LibroTrack, kullanıcıların kişisel kitap koleksiyonlarını yönetmelerini, okuma alışkanlıklarını takip etmelerini, kitap notlarını saklamalarını ve okuma verileri üzerinde analizler gerçekleştirmelerini sağlayan CLI tabanlı bir Python uygulamasıdır. Uygulama SQLite veritabanı kullanır ve ek olarak stres testi, benchmark, Monte Carlo testi ve sinyal tabanlı veri görselleştirme gibi araçlar içerir.

---

# Özellikler

- Kullanıcı ekleme, silme ve listeleme
- Kitap ekleme, silme ve güncelleme
- Kitap arama (başlık veya yazar)
- Kitapları tür ve okuma durumuna göre filtreleme
- Okuma durumu takibi (okunacak, okunuyor, okundu)
- Kitaplara not ekleme
- Belirli bir kitaba ait notları listeleme
- Kullanıcının tüm kitap notlarını listeleme
- Okuma özeti oluşturma
- Tür dağılımı pasta grafiği oluşturma (.png)
- Okunan kitapları CSV dosyasına aktarma (.csv)
- Okuma aktivitesi sinyal grafiği oluşturma (.png)
- Stress Test
- Benchmark Testi (CSV ve grafik çıktısı)
- Monte Carlo Testi
- Logging desteği
- YAML tabanlı konfigürasyon desteği
- Pytest ile birim testleri

---

# Kurulum

## Gereksinimler

- Python 3.10 veya üzeri

## Kurulum Adımları

1. Projeyi bilgisayarınıza indirin veya klonlayın.

2. Gerekli kütüphaneleri yükleyin.

```bash
pip install -r requirements.txt
```

3. Proje kök dizininde bulunan `config.yaml` dosyasını isteğe bağlı olarak düzenleyebilirsiniz.

```yaml
database:
  path: librotrack.db

logging:
  console_level: INFO
  file_level: DEBUG
  file: librotrack.log
```

---

# Kullanım

Tüm komutlar aşağıdaki formatta çalıştırılır:

```bash
python libro.py <komut> [parametreler]
```

---

# Kullanıcı İşlemleri

```bash
# Kullanıcı ekle
python libro.py kullanici-ekle --kullanici ali

# Kullanıcı sil
python libro.py kullanici-sil --kullanici ali

# Sistemde kayıtlı kullanıcıları listele
python libro.py kullanici-listele
```

---

# Kitap İşlemleri

```bash
# Kitap ekle
python libro.py kitap-ekle --kullanici ali --baslik "Dune" --yazar "Frank Herbert" --isbn "222" --tur "Bilim Kurgu" --sayfa-sayisi 430

# Kitap sil
python libro.py kitap-sil --kullanici ali --isbn "222"

# Kitap bilgilerini güncelle
python libro.py kitap-guncelle --kullanici ali --isbn "222" --tur "Klasik" --sayfa-sayisi 450

# Tüm kitapları listele
python libro.py kitap-listele --kullanici ali

# Türe göre filtrele
python libro.py kitap-listele --kullanici ali --tur "Bilim Kurgu"

# Duruma göre filtrele
python libro.py kitap-listele --kullanici ali --durum okundu

# Başlık veya yazara göre ara
python libro.py kitap-ara --kullanici ali --anahtar-kelime "Frank"
```

---

# Okuma Takibi ve Notlar

```bash
# Okuma durumunu güncelle
python libro.py durum-guncelle --kullanici ali --isbn "222" --durum okunuyor

python libro.py durum-guncelle --kullanici ali --isbn "222" --durum okundu

# Kitaba not ekle
python libro.py not-ekle --kullanici ali --isbn "222" --not-metni "Not denemesi." --sayfa 12

# Belirli bir kitaba ait notları listele
python libro.py notlari-listele --kullanici ali --isbn "222"

# Kullanıcının tüm notlarını listele
python libro.py tum-notlari-listele --kullanici ali
```

---

# İstatistik ve Raporlama

```bash
# Okuma özeti
python libro.py ozet --kullanici ali

# Tür dağılımı grafiği oluştur
python libro.py tur-dagilimi --kullanici ali

# Özel dosya adı ile kaydet
python libro.py tur-dagilimi --kullanici ali --dosya grafik.png

# Okunan kitapları CSV'ye aktar
python libro.py csv-aktar --kullanici ali

# Özel dosya adı ile kaydet
python libro.py csv-aktar --kullanici ali --dosya kitaplar.csv

# Okuma aktivitesi sinyal grafiği oluştur
python libro.py reading-signal --kullanici ali
```

---

# Performans Analizi

LibroTrack yalnızca bir kütüphane yönetim sistemi değildir; aynı zamanda sistem performansını değerlendirmek amacıyla çeşitli test modülleri de içermektedir.

```bash
# Stress Test
python libro.py stress-test

# Özel parametrelerle Stress Test
python libro.py stress-test --kullanici-sayisi 100 --kitap-sayisi 50

# Benchmark Testi
python libro.py benchmark

# Farklı kitap sayıları ile benchmark
python libro.py benchmark --kitap-sayilari 100 500 1000 5000

# Monte Carlo Testi
python libro.py monte-carlo

# Özel parametrelerle Monte Carlo
python libro.py monte-carlo --runs 50 --max-users 20 --max-books 40
```

Bu testlerin amacı:

- **Stress Test:** Sistemin çok sayıda kullanıcı ve kitap ile çalışırken kararlılığını ölçer.
- **Benchmark:** Artan kitap sayılarında ekleme performansını ölçerek CSV ve grafik çıktısı oluşturur.
- **Monte Carlo Testi:** Rastgele oluşturulan çok sayıda senaryo üzerinde sistem davranışını analiz eder.
- **Reading Signal:** Kullanıcının tamamladığı kitaplardan oluşan okuma aktivitesi sinyalini oluşturur. Okunan sayfa sayısını günlere bağlı olan bir discrete sinyal olarak .png dosyası halinde gösterir.

---

# Sistem İşlemleri

```bash
# Tüm verileri sıfırla
python libro.py sifirla
```

Komut çalıştırıldığında sistem ikinci bir onay isteyerek yanlışlıkla veri kaybını önlemektedir.

---

# Proje Yapısı

```text
librotrack/
│
├── libro.py                 # CLI giriş noktası
├── config.yaml              # Konfigürasyon dosyası
├── requirements.txt         # Bağımlılıklar
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── models.py            # Kitap ve Kullanici sınıfları
│   ├── database.py          # SQLite işlemleri
│   ├── library.py           # Ana iş mantığı (Kutuphane)
│   ├── exceptions.py        # Özel hata sınıfları
│   ├── config.py            # config.yaml okuma
│   └── test_additions.py    # Stress, Benchmark ve Monte Carlo testleri
│
└── tests/
    ├── __init__.py
    └── test_library.py      # Pytest birim testleri
```

---

# Konfigürasyon

Uygulama başlangıcında `config.yaml` dosyası okunarak veritabanı yolu ve loglama ayarları otomatik olarak yüklenmektedir.

| Alan | Açıklama | Varsayılan |
|------|----------|------------|
| `database.path` | SQLite veritabanı dosyası | `librotrack.db` |
| `logging.console_level` | Konsol log seviyesi | `INFO` |
| `logging.file_level` | Dosya log seviyesi | `DEBUG` |
| `logging.file` | Log dosyası | `librotrack.log` |

---

# Loglama

Uygulama Python'un **logging** modülünü kullanmaktadır.

- INFO ve üzerindeki loglar terminale yazdırılır.
- DEBUG ve üzerindeki loglar `librotrack.log` dosyasına kaydedilir.
- Her log kaydı aşağıdaki bilgileri içerir:

```
Tarih Saat | Log Seviyesi | Modül | Mesaj
```

Loglama sayesinde kullanıcı işlemleri, hata kayıtları ve önemli sistem olayları daha sonra incelenebilir.

---

# Birim Testler

Projede **pytest** kullanılarak geliştirilen 19 bağımsız birim testi bulunmaktadır.

Test edilen başlıca işlemler:

- Kullanıcı ekleme
- Kullanıcı silme
- Kitap ekleme
- Kitap silme
- Kitap güncelleme
- Okuma durumu güncelleme
- Not ekleme
- Kitap arama
- CSV oluşturma
- Grafik oluşturma
- Benzersizlik kontrolleri
- Veritabanı sıfırlama
- Özet oluşturma

Testleri çalıştırmak için:

```bash
python -m pytest tests/test_library.py
```

---

# Hata Kodları

| Kod | Açıklama |
|------|----------|
| `0` | İşlem başarıyla tamamlandı. |
| `1` | Bir hata oluştu ve hata mesajı kullanıcıya gösterildi. |

---

# Bağımlılıklar

| Kütüphane | Versiyon | Amaç |
|-----------|----------|------|
| matplotlib | 3.7.2 | Grafik oluşturma |
| pytest | 7.4.0 | Birim testleri |
| PyYAML | 6.0 | Konfigürasyon dosyasını okuma |

---