from src.database import VeritabaniYoneticisi
from src.library import Kutuphane

db = VeritabaniYoneticisi("test_librotrack.db")
kutuphane = Kutuphane(db)

kutuphane.kullanici_ekle("ali")

kutuphane.kitap_ekle(
    kullanici_adi="ali",
    baslik="Dune",
    yazar="Frank Herbert",
    isbn="123",
    tur="Sci-Fi",
    sayfa_sayisi=500
)

print(kutuphane.kitaplari_listele("ali"))

kutuphane.durum_guncelle("ali", "123", "okundu")

kutuphane.not_ekle(
    kullanici_adi="ali",
    isbn="123",
    not_metni="Good opening chapter.",
    not_sayfasi=12
)

print(kutuphane.notlari_listele("ali", "123"))

kutuphane.kitap_guncelle(
    kullanici_adi="ali",
    isbn="123",
    tur="Science Fiction"
)

print(kutuphane.kitaplari_listele("ali"))

kutuphane.kitap_sil("ali", "123")
print(kutuphane.kitaplari_listele("ali"))