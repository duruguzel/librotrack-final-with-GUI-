""" 
Kütüphane logic (main)
"""

import matplotlib.pyplot as plt
import logging
import csv
import re
from datetime import datetime, date

from src.database import VeritabaniYoneticisi
from src.models import Kitap
from src.exceptions import KitapBulunamadi, hatali_bilgi

logger = logging.getLogger(__name__)

class Kutuphane:
    """Kullanıcıların kitap koleksiyonlarını kontrol eden sınıf.
    Her kullanıcı için kitap işlemlerini koordine eder. 
    Veritabanı işlemleri VeritabaniYoneticisi üzerinden gerçekleştirilir.
    """
    def __init__(self, db: VeritabaniYoneticisi):
        """
        Parameters
        ----------
        db : VeritabaniYoneticisi
            Veritabanı işlemlerini yürütecek nesne.

        Returns
        -------
        None.

        """
        self.db = db
    
    
    def kitap_ekle(self, kullanici_adi:str, baslik:str, yazar:str, isbn:str, tur:str, sayfa_sayisi:int) -> None:
        """ Seçili kullanıcının kütüphanesine yeni bir kitap ekler.
        
        Parameters
        ----------
        kullanici_adi : str
            Kitabı ekleyen kullanıcının ismi.
        baslik : str
            Eklenen kitabın başlığı.
        yazar : str
            Eklenen kitabın yazarı.
        isbn : str
            Eklenen kitabın ISBN'si.
        tur : str
            Eklenen kitabın türü.
        sayfa_sayisi : int
            Eklenen kitabın sayfa sayısı.

        Returns
        -------
        None
        """
        kullanici_id = self.db.kullanici_bul(kullanici_adi)
        kitap = Kitap(baslik=baslik, yazar=yazar, isbn=isbn, tur=tur, sayfa_sayisi=sayfa_sayisi)
        self.db.kitap_ekle(kitap, kullanici_id)
        logger.info("Kitap eklendi: %s", isbn)


    def kullanici_ekle(self, kullanici_adi:str) -> None:
        """ Sisteme yeni bir kullanıcı ekler.
        
        Parameters
        ----------
        kullanici_adi : str
            Eklenen kullanıcının ismi.

        Returns
        -------
        None
        """
        self.db.kullanici_ekle(kullanici_adi)
        logger.info("Kullanıcı eklendi: %s", kullanici_adi)


    def kitap_sil(self, kullanici_adi:str, isbn:str) -> None:
        """ Belirtilen kullanıcının kütüphanesinden seçilen kitabı siler.
        
        Parameters
        ----------
        kullanici_adi : str
            Kitabı silen kullanıcının ismi.
        isbn : str
            Silinecek kitabın ISBN'si.

        Returns
        -------
        None
        """
        kullanici_id = self.db.kullanici_bul(kullanici_adi)
        self.db.kitap_sil(kullanici_id, isbn)
        logger.info("Kitap silindi: %s", isbn)
        
        
    def kullanici_sil(self, kullanici_adi:str) -> None:
        """ Kullanıcıyı ve ona ait tüm kitap ve notları sistemden siler.
        
        Parameters
        ----------
        kullanici_adi : str
            Silinecek kullanıcının ismi.

        Returns
        -------
        None
        """
        kullanici_id = self.db.kullanici_bul(kullanici_adi)
        self.db.kullanici_sil(kullanici_id)
        logger.info("Kullanıcı silindi: %s", kullanici_adi)
        
        
    def kitap_guncelle(self, kullanici_adi:str, isbn:str, baslik:str | None = None, 
                       yazar:str | None = None, tur:str | None = None, sayfa_sayisi:int | None = None) -> None:
        """Belirtilen kitabın bilgilerini günceller (hatalı girme durumları için). ISBN güncellenemez.
        
        Parameters
        ----------
        kullanici_adi : str
            Güncelleme yapan kullanıcının ismi.
        isbn : str
            Güncellenecek kitabın ISBN'si.
        baslik : str | None, optional
            Yeni başlık. The default is None.
        yazar : str | None, optional
            Yeni yazar. The default is None.
        tur : str | None, optional
            Yeni tür. The default is None.
        sayfa_sayisi : int | None, optional
            Yeni sayfa sayısı. The default is None.

        Returns
        -------
        None
        """
        kullanici_id = self.db.kullanici_bul(kullanici_adi)
        self.db.kitap_guncelle(isbn=isbn, kullanici_id=kullanici_id, baslik=baslik, yazar=yazar, sayfa_sayisi=sayfa_sayisi, tur=tur)
        logger.info("Kitap güncellendi: %s", isbn)
        
        
    def durum_guncelle(self, kullanici_adi:str, isbn:str, yeni_durum:str) -> None:
        """Belirtilen kitabın okunma durumunu günceller.
        
        Parameters
        ----------
        kullanici_adi : str
            Durum güncellemesi yapan kullanıcının ismi.
        isbn : str
            Durum güncellemesi yapılan kitabın ISBN'si.
        yeni_durum : str
            Yeni durum (okunacak, okunuyor, okundu).

        Returns
        -------
        None
        """
        kullanici_id = self.db.kullanici_bul(kullanici_adi)
        self.db.durum_guncelle(isbn=isbn, kullanici_id=kullanici_id, durum=yeni_durum)
        logger.info("%s kitabının durumu %s olarak güncellendi", isbn, yeni_durum)
        
        
    def kitaplari_listele(self, kullanici_adi:str, tur:str | None = None, 
                          durum:str | None = None) -> list[tuple]:
        """Belirtilen kullanıcının kütüphanesindeki kayıtlı kitapları listeler.
        
        Parameters
        ----------
        kullanici_adi : str
            Kitapları listelenecek kullanıcının adı.
        tur : str | None, optional
            Verilen üre göre filtrelenip sıralama. The default is None.
        durum : str | None, optional
            Verilen duruma göre filtrelenip sıralama. The default is None.

        Returns
        -------
        list[tuple]
            Her biri (id, baslik, yazar, isbn, tur, sayfa_sayisi, durum, bitis_tarihi)
            sırasıyla içeren tuple'lardan oluşan liste.

        """
        kullanici_id = self.db.kullanici_bul(kullanici_adi)
        return self.db.kitaplari_listele(kullanici_id, tur=tur, durum=durum)
        
        
    def not_ekle(self, kullanici_adi:str, isbn:str,  not_metni:str, not_sayfasi:int | None = None) -> None:
        """Belirtilen kitaba not ekler.
        
        Parameters
        ----------
        kullanici_adi : str
            Kitabın sahibi olan kullanıcının ismi.
        isbn : str
            Not eklenecek kitabın ISBN'si.
        not_metni : str
            Eklenen not metni.
        not_sayfasi : int | None, optional
            Not eklenen sayfa numarası. The default is None.

        Returns
        -------
        None
        """
        kullanici_id = self.db.kullanici_bul(kullanici_adi)
        self.db.not_ekle(isbn=isbn, kullanici_id=kullanici_id, not_metni=not_metni, sayfa=not_sayfasi)
        logger.info("Not eklendi. ISBN: %s", isbn)
        
    
    def notlari_listele(self, kullanici_adi:str, isbn:str) -> list[tuple]:
        """Belirtilen kitaptaki tüm notları listeler.
        
        Parameters
        ----------
        kullanici_adi : str
            Notların sahibi olan kullanıcının ismi.
        isbn : str
            Notların eklendiği kitabın ISBN'si.

        Returns
        -------
        list[tuple]
            Her biri (not_id, kitap_id, not_metni, sayfa) sırasıyla 
            içeren tuple'lardan oluşan liste.

        """
        kullanici_id = self.db.kullanici_bul(kullanici_adi)
        return self.db.notlari_listele(isbn=isbn, kullanici_id=kullanici_id)
    
    
    def tum_notlari_listele(self, kullanici_adi:str) -> list[tuple]:
        """Bir kullanıcıya ait tüm notları listeler.
        
        Parameters
        ----------
        kullanici_adi : str
            Seçili kullanıcının adı.

        Returns
        -------
        list[tuple]
            Belirtilen kullanıcıya ait tüm notları, her biri 
            (not_id, baslik, isbn, not_metni, sayfa) sırasıyla içeren 
            tuple'lardan oluşan bir liste olarak döndürür.

        """
        kullanici_id = self.db.kullanici_bul(kullanici_adi)
        return self.db.tum_notlari_listele(kullanici_id)
        
    
    def kitap_ara(self, kullanici_adi:str, anahtar_kelime:str) -> list[tuple]:
        """Başlık veya yazar isimlerinde verilen anahtar kelimeyi içeren kitapları arar
        
        Parameters
        ----------
        kullanici_adi : str
            Kitabın sahibi olan kullanıcının ismi.
        anahtar_kelime : str
            Aranacak kelime veya kelime parçası.

        Returns
        -------
        list[tuple]
            Her biri (id, kullanici_id, baslik, yazar, isbn, tur, sayfa_sayisi, durum, bitis_tarihi)
            sırasıyla içeren tuple'lardan oluşan liste..

        """
        kullanici_id = self.db.kullanici_bul(kullanici_adi)
        tum_kitaplar = self.db.kitaplari_listele(kullanici_id)
        
        try:
            pattern = re.compile(anahtar_kelime, re.IGNORECASE)
        except re.error:
            raise hatali_bilgi("Geçersiz arama ifadesi")
            
        return [
            kitap for kitap in tum_kitaplar
            if pattern.search(kitap[1]) or pattern.search(kitap[2])]
        
    
    def tur_dagilimi_grafigi(self, kullanici_adi:str, dosya_adi:str = "tur_dagilimi.png")-> None:
        """Kullanıcının kitaplığındaki tür dağılımını pasta grafiği olarak kaydeder.
        
        Parameters
        ----------
        kullanici_adi : str
            Grafiği oluşturulacak kullanıcının adı.
        dosya_adi : str, optional
            Grafiğin kaydedileceği dosyanın adı. The default is "tur_dagilimi.png".

        Raises
        ------
        KitapBulunamadi
            Grafik oluşturmak için yeterli kitap bulunamazsa.

        Returns
        -------
        None
        """
        kullanici_id =self.db.kullanici_bul(kullanici_adi)
        dagilim = self.db.tur_dagilimi(kullanici_id)
        
        if not dagilim:
            raise KitapBulunamadi("Grafik oluşturmak için kitap bulunamadı")
            
        turler = [satir[0] for satir in dagilim]
        sayilar = [satir[1] for satir in dagilim]
        
        plt.figure()
        plt.pie(sayilar, labels=turler, autopct="%1.1f%%")
        plt.title(f"Kitap Tür Dağılımı ({kullanici_adi})")
        plt.savefig(dosya_adi)
        plt.close()
        
        logger.info("Tür dağılımı grafiği oluşturuldu: %s", dosya_adi)
        
        
    def ozet_goster(self, kullanici_adi:str) -> tuple:
        """ Kullanıcının okuma istatistiklerini özet olarak döndürür.
        
        Parameters
        ----------
        kullanici_adi : str
            İstatistikleri gösterilecek olan kullanıcının adı.

        Returns
        -------
        tuple
            (toplam_kitap, okunan_kitap, toplam_sayfa) sırasıyla içeren tuple.

        """
        kullanici_id = self.db.kullanici_bul(kullanici_adi)
        return self.db.ozet_bilgisi(kullanici_id)
    
    
    def okunan_kitaplari_csv_aktar(self, kullanici_adi: str, dosya_adi: str = "okunan_kitaplar.csv") -> None:
        """Kullanıcının okuduğu kitapları CSV dosyasına aktarır
        
        Parameters
        ----------
        kullanici_adi : str
            Kitapları CSV dosyasına aktarılacak kullanıcının adı.
        dosya_adi : str, optional
            Oluşturulan CSV soyasının adı. The default is "okunan_kitaplar.csv".

        Returns
        -------
        None
        """
        kullanici_id = self.db.kullanici_bul(kullanici_adi)
        kitaplar = self.db.okunan_kitaplari_getir(kullanici_id)
        
        try:
            with open(dosya_adi, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)  
                writer.writerow(["baslik", "yazar", "isbn", "tur", "sayfa_sayisi", "bitis_tarihi"])
                writer.writerows(kitaplar)
            logger.info("Okunan kitaplar CSV dosyasına aktarıldı: %s", dosya_adi)
        except OSError as error:
            logger.error("CSV dosyası yazılamadı: %s", error)
    
        
    def sifirla(self) -> None:
        """ Veritabanındaki tüm kullanıcı, kitap ve not verilerini siler.

        Returns
        -------
        None
        """
        self.db.sifirla()
        logger.info("Veritabanı sıfırlandı")
        
   
    def okuma_sinyali_grafigi(self, kullanici_adi:str, dosya_adi: str="reading_signal.png") -> None:
        """Kullanıcının okuma alışkanlıklarını göstermek üzere kitapların tamamlandıkları gün 
        ve uzunluklarının gösterildiği bir grafik oluşturur.

        Parameters
        ----------
        kullanici_adi : str
            İncelenen kullanıcının adı.
        dosya_adi : str, optional
            Oluşturulan grafiğin kaydedildiği dosyanın adı. The default is "reading_signal.png".

        Raises
        ------
        KitapBulunamadi
            Belirtilen kullanıcının kütüphanesinde bitmiş bir kitap yoksa.

        Returns
        -------
        None
        """
        kullanici_id=self.db.kullanici_bul(kullanici_adi)
        veri = self.db.okuma_sinyali_verisi(kullanici_id)
        
        if not veri:
            raise KitapBulunamadi("Okuma sinyali oluşturmak için okunan kitap bulunamadı")
        
        tarihler = []
        
        for satir in veri:
            tarih = satir[0]
        
            if isinstance(tarih, str):
                tarihler.append(datetime.fromisoformat(tarih))
            else:
                tarihler.append(tarih)        
        sayfalar = [satir[1] for satir in veri]
        
        plt.figure()
        markerline, stemlines, baseline = plt.stem(tarihler, sayfalar)
        plt.setp(markerline, markersize=8)
        plt.setp(stemlines, linewidth=2)
        plt.xticks(tarihler)  #x ekseninde sadece tamamlanan tarihler görünür (hepsi yerine)
        plt.xlabel("Tarih")
        plt.ylabel("Tamamlanan Sayfa")
        plt.title(f"Okuma Aktivitesi Sinyali ({kullanici_adi})")
        plt.grid(True, axis="y")
        plt.tight_layout()
        plt.savefig(dosya_adi)
        plt.close()
        
        logger.info("Okuma sinyali grafiği oluşturuldu: %s", dosya_adi)
        
        
    def kullanicilari_listele(self) -> list[tuple]:
        """Sistemdeki tüm kullanıcıları listeler.

        Returns
        -------
        list[tuple]
            Sistemde kayıtlı kullanıcıları liste olarak döndürür.

        """
        
        return self.db.kullanicilari_listele()
    
    
    def kullanici_bul(self, kullanici_adi: str) -> int:
        """Checks whether a user exists and returns the user's ID."""
        return self.db.kullanici_bul(kullanici_adi)
    
    