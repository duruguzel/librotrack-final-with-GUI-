"""
Kitap, Kullanıcı classes
"""

from src.exceptions import hatali_bilgi


durumlar = ["okunacak", "okunuyor", "okundu"]


class Kitap:
    """Kütüphanedeki bir kitabı temsil eden sınıf"""
    toplam_kitap_sayisi = 0
    def __init__(self, baslik, yazar, isbn, tur, sayfa_sayisi, durum="okunacak", bitis_tarihi=None, kitap_id=None):
        
        if sayfa_sayisi <= 0:
            raise hatali_bilgi("Sayfa sayısı pozitif olmalı.")
        if durum not in durumlar:
            raise hatali_bilgi("Geçersiz durum girildi.")

        self.baslik = baslik
        self.yazar = yazar
        self.isbn = isbn
        self.tur = tur
        self.sayfa_sayisi = sayfa_sayisi
        self.durum = durum
        self. bitis_tarihi= bitis_tarihi
        self.kitap_id = kitap_id
        Kitap.toplam_kitap_sayisi += 1
        
        
    @property  #Allows you to call the function and get the value without parenthesis.
    def tamamlanma(self) -> bool:
        """
        Returns
        -------
        bool
            Kitabın okunup okunmadığını döndürür (True / False).

        """
        return self.durum == "okundu"
    
    def __repr__(self) -> str:
        return f"Kitap('{self.baslik}','{self.yazar}', ISBN: {self.isbn})"


class Kullanici:
    """Sistemdeki bir kullanıcıyı temsil eden sınıf"""
    def __init__(self, kullanici_adi, kullanici_id=None):
        self.kullanici_adi = kullanici_adi
        self.kullanici_id = kullanici_id
        
    def __repr__(self) -> str:
        return f"Kullanici('{self.kullanici_adi}')"
    
        