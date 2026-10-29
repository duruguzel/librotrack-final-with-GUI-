"""
Unit tests for the Kutuphane class using pytest.
Each test uses a temporary SQLite database and is independent of the others.
"""

import pytest

from src.database import VeritabaniYoneticisi
from src.library import Kutuphane
from src.exceptions import ISBN_mevcut, KitapBulunamadi, KullaniciBulunamadi, kullanici_mevcut, hatali_bilgi


@pytest.fixture
def kutuphane(tmp_path):
    db_path = tmp_path / "test_librotrack.db"
    db = VeritabaniYoneticisi(str(db_path))
    return Kutuphane(db)


def test_kullanici_ekle(kutuphane):
    kutuphane.kullanici_ekle("ali")
    kullanici_id = kutuphane.db.kullanici_bul("ali")
    assert isinstance(kullanici_id, int)


#zaten kayıtlı olan bir kullanıcı tekrar eklenemez
def test_ayni_kullanici_eklenemez(kutuphane):
    kutuphane.kullanici_ekle("ali")
    
    with pytest.raises(kullanici_mevcut):
        kutuphane.kullanici_ekle("ali")
        

def test_kitap_ekle(kutuphane):
    kutuphane.kullanici_ekle("ali")
    kutuphane.kitap_ekle("ali","Dune","Frank Herbert", "123", "bilim kurgu", 500)
    kitaplar = kutuphane.kitaplari_listele("ali")
    
    assert len(kitaplar) == 1
    assert kitaplar[0][1] == "Dune"
    

#aynı kitap aynı kullanıcıda tekrar eklenemez
def test_ayni_isbn(kutuphane):
    kutuphane.kullanici_ekle("ali")
    kutuphane.kitap_ekle("ali","Dune","Frank Herbert", "123", "bilim kurgu", 500)
    
    with pytest.raises(ISBN_mevcut):
        kutuphane.kitap_ekle("ali","Dune","Frank Herbert", "123", "bilim kurgu", 500)
        

#aynı kitap farklı kullanıcılarda eklenebilir        
def test_ayni_isbn_farkli_kullanici(kutuphane):
    kutuphane.kullanici_ekle("ali")
    kutuphane.kullanici_ekle("ayse")
    kutuphane.kitap_ekle("ali", "Dune", "Frank Herbert", "123", "bilim kurgu", 500)
    kutuphane.kitap_ekle("ayse", "Dune", "Frank Herbert", "123", "bilim kurgu", 500)
    
    assert len(kutuphane.kitaplari_listele("ali")) == 1
    assert len(kutuphane.kitaplari_listele("ayse")) == 1


def test_kitap_sil(kutuphane):
    kutuphane.kullanici_ekle("ali")
    kutuphane.kitap_ekle("ali", "Dune", "Frank Herbert", "123", "bilim kurgu", 500)
    kutuphane.kitap_sil("ali", "123")
    assert kutuphane.kitaplari_listele("ali") == []
    

#kayıtlı olmayan bir isbn'li kitap silinemez    
def test_olmayan_kitap_sil(kutuphane):
    kutuphane.kullanici_ekle("ali")
    
    with pytest.raises(KitapBulunamadi):
        kutuphane.kitap_sil("ali","5")
        

def test_durum_guncelle(kutuphane):
    kutuphane.kullanici_ekle("ali")
    kutuphane.kitap_ekle("ali", "Dune", "Frank Herbert", "123", "bilim kurgu", 500)
    kutuphane.durum_guncelle("ali", "123", "okundu")
    kitaplar = kutuphane.kitaplari_listele("ali")
    
    assert kitaplar[0][6] == "okundu"
    assert kitaplar[0][7] is not None
    
    
def test_not_ekle_listele(kutuphane):
    kutuphane.kullanici_ekle("ali")
    kutuphane.kitap_ekle("ali", "Dune", "Frank Herbert", "123", "bilim kurgu", 500)
    kutuphane.not_ekle("ali", "123", "Not denemesi", 50)
    notlar = kutuphane.notlari_listele("ali", "123")
    
    assert len(notlar) == 1
    assert notlar[0][2] == "Not denemesi"
    assert notlar[0][3] == 50


#sayfa numarası negatif olamaz 
def test_hatali_sayfa(kutuphane):
    kutuphane.kullanici_ekle("ali")
    
    with pytest.raises(hatali_bilgi):
        kutuphane.kitap_ekle("ali", "Iliad", "Homer", "999", "destan", -10)
        

def test_kullanici_sil(kutuphane):
    kutuphane.kullanici_ekle("ali")
    kutuphane.kullanici_sil("ali")                      
    with pytest.raises(KullaniciBulunamadi):
        kutuphane.db.kullanici_bul("ali")
        

#durumu okunacak olan kitaba not eklenirse durum okunuyor olarak güncellenir       
def test_not_durum_değişimi(kutuphane):
    kutuphane.kullanici_ekle("ali")
    kutuphane.kitap_ekle("ali", "Dune", "Frank Herbert", "123", "bilim kurgu", 500)
    kutuphane.not_ekle("ali", "123", "Note", 100)
    kitaplar = kutuphane.kitaplari_listele("ali")
    assert kitaplar[0][6] == "okunuyor"


#anahtar kelime olarak başlık kullanılarak kitap arama
def test_kitap_ara_baslik(kutuphane):
    kutuphane.kullanici_ekle("ali")
    kutuphane.kitap_ekle("ali", "Dune", "Frank Herbert", "123", "bilim kurgu", 500)
    sonuc = kutuphane.kitap_ara("ali", "Du")
    assert len(sonuc) == 1
    

#anahtar kelime olarak yazar kullanılarak kitap arama    
def test_kitap_ara_yazar(kutuphane):
    kutuphane.kullanici_ekle("ali")
    kutuphane.kitap_ekle("ali", "Dune", "Frank Herbert", "123", "bilim kurgu", 500)
    sonuc = kutuphane.kitap_ara("ali", "Frank")
    assert  len(sonuc) == 1
    
    
def test_ozet(kutuphane):
    kutuphane.kullanici_ekle("ali")
    kutuphane.kitap_ekle("ali", "Dune", "Frank Herbert", "123", "bilim kurgu", 500)
    kutuphane.durum_guncelle("ali","123","okundu")
    toplam, okunan, sayfa = kutuphane.ozet_goster("ali")

    assert toplam == 1
    assert okunan == 1
    assert sayfa == 500
    
    
def test_csv(kutuphane, tmp_path):
    kutuphane.kullanici_ekle("ali")
    kutuphane.kitap_ekle("ali","Dune","Frank Herbert", "123", "bilim kurgu", 500)
    kutuphane.durum_guncelle("ali", "123", "okundu")
    
    dosya = tmp_path / "okunan.csv"
    kutuphane.okunan_kitaplari_csv_aktar("ali", str(dosya))
    
    assert dosya.exists()
    
    
#sistem sıfırlandığında kullanıcılara ait tüm bilgilerin silinmesi
def test_sifirlama(kutuphane):
    kutuphane.kullanici_ekle("ali")
    kutuphane.kitap_ekle("ali","Dune","Frank Herbert", "123", "bilim kurgu", 500)
    
    assert len(kutuphane.kitaplari_listele("ali")) == 1
    
    kutuphane.sifirla()
    
    with pytest.raises(KullaniciBulunamadi):
        kutuphane.db.kullanici_bul("ali")


def test_ozet_2(kutuphane):
    kutuphane.kullanici_ekle("ali")
    kutuphane.kitap_ekle("ali","Dune","Frank Herbert", "123", "bilim kurgu", 500)
    kutuphane.kitap_ekle("ali","Iliad","Homer", "111", "destan", 300)
    kutuphane.durum_guncelle("ali","123","okundu")
    kutuphane.durum_guncelle("ali","111","okundu")
    toplam, okunan, sayfa = kutuphane.ozet_goster("ali")

    assert toplam == 2
    assert okunan == 2
    assert sayfa == 800
    
    
def test_ozet_3(kutuphane):
    kutuphane.kullanici_ekle("ali")
    kutuphane.kitap_ekle("ali","Dune","Frank Herbert", "123", "bilim kurgu", 500)
    kutuphane.kitap_ekle("ali","Iliad","Homer", "111", "destan", 300)
    kutuphane.kitap_ekle("ali","Odyssey","Homer", "222", "destan", 200)
    kutuphane.durum_guncelle("ali","123","okundu")
    kutuphane.durum_guncelle("ali","111","okundu")
    toplam, okunan, sayfa = kutuphane.ozet_goster("ali")

    assert toplam == 3
    assert okunan == 2
    assert sayfa == 800
