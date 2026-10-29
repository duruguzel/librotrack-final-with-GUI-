"""
SQLite connection + VeritabanıYöneticisi class
"""

import sqlite3
from datetime import date

from src.exceptions import VeritabaniHatasi, ISBN_mevcut, KitapBulunamadi, kullanici_mevcut, KullaniciBulunamadi
from src.models import Kitap


class VeritabaniYoneticisi:
    def __init__(self, db_path: str = "librotrack.db"):    #creating the database (or opening the existing)
        self.db_path = db_path
        self.tablolari_olustur()  #ilk runlamada tablolar otomatik oluşuyor
      
        
    def baglan(self)  -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Veritabanına bağlanılamadı") from error
    
    
    def tablolari_olustur(self) -> None:
        try:
            with self.baglan() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                        CREATE TABLE IF NOT EXISTS kullanicilar (
                            kullanici_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            kullanici_adi TEXT UNIQUE NOT NULL)""")
                #her kullanici için: kullanıcı id, kullanıcı adı
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS kitaplar (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        kullanici_id INTEGER NOT NULL,
                        baslik TEXT NOT NULL,
                        yazar TEXT NOT NULL,
                        isbn TEXT NOT NULL,
                        tur TEXT,
                        sayfa_sayisi INTEGER NOT NULL,
                        durum TEXT DEFAULT 'okunacak',
                        bitis_tarihi TEXT,
                        UNIQUE (kullanici_id, isbn),
                        FOREIGN KEY (kullanici_id)
                            REFERENCES kullanicilar(kullanici_id)
                            ON DELETE CASCADE)""")
                #each book gets an id depending on the time they were added (autoincremented)
                #isbn is stored as text bc we dont perform arithmetics on them / they act as quantities
                #her kitap için: id, kullanıcı id, başlık, yazar, isbn, tür,sayfa sayısı, durum, bitiş tarihi
                #isbn ve kullanıcı id (ikisi aynı anda) aynı olamıyor (aynı kişi aynı kitabı 2 kere giremiyor)

                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notlar (
                        not_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        kitap_id INTEGER NOT NULL,
                        not_metni TEXT NOT NULL,
                        sayfa INTEGER,
                        FOREIGN KEY (kitap_id)
                            REFERENCES kitaplar(id)
                            ON DELETE CASCADE)""")
                #her not için: not id, kitap id, not metni, sayfa
                
                
                conn.commit()
        
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Tablo oluşturulamadı") from error
        
  
    def kullanici_ekle(self, kullanici_adi: str) -> int:  #returns the last row id (an integer)
        """Verilen kullanıcıyı sisteme ekler (adı ile).
        
        Parameters
        ----------
        kullanici_adi : str
            Eklenecek olan kullanıcının ismi.

        Raises
        ------
        kullanici_mevcut
            Belirtilen kullanıcı sisteme önceden kaydedilmiş.
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.

        Returns
        -------
        int
            Kullanıcının ID numarası (kullanici_id).

        """
        try:
            with self.baglan() as conn:
                cursor = conn.cursor()
                    
                cursor.execute("""
                                   INSERT INTO kullanicilar (kullanici_adi)
                                   VALUES(?)""",
                                   (kullanici_adi,))
                conn.commit()
                return cursor.lastrowid
                
        except sqlite3.IntegrityError:
            raise kullanici_mevcut("Bu kullanıcı zaten sisteme eklenmiş.")
                    
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Kullanıcı eklenemedi") from error
     
            
    def kitap_ekle(self, kitap: Kitap, kullanici_id:int) ->None:
        """Verilen kitabı seçili kullanıcının kütüphanesine ekler.

        Parameters
        ----------
        kitap : Kitap
            Eklenen kitabın özellikleri (baslik, yazar, isbn, tur, sayfa_sayisi, durum, bitis_tarihi).
        kullanici_id : int
            Kullanıcı ID numarası.

        Raises
        ------
        ISBN_mevcut
            Verilen ISBN'ye sahip olan kitap seçili kullanıcı tarafından önceden kaydedilmiş.
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.

        Returns
        -------
        None

        """
        try:
            with self.baglan() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                               INSERT INTO kitaplar(
                                   kullanici_id, baslik, yazar,isbn, 
                                   tur, sayfa_sayisi, durum, bitis_tarihi)
                               VALUES(?,?,?,?,?,?,?,?)""",
                               (kullanici_id, kitap.baslik, kitap.yazar,
                                kitap.isbn, kitap.tur, kitap.sayfa_sayisi,
                                kitap.durum, kitap.bitis_tarihi))
                conn.commit()
                
        except sqlite3.IntegrityError as error:
            raise ISBN_mevcut("Seçili kullanıcı bu ISBN'ye sahip kitabı önceden eklemiş.") from error
        
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Kitap eklenemedi") from error
          
            
    def kullanici_bul(self, kullanici_adi:str) -> int:
        """Aranan kullanıcının sistemde olup olmadığını inceler ve 
        bulunan kullanıcının ID numarasını döndürür.
        
        Parameters
        ----------
        kullanici_adi : str
            Kullanıcının ismi.

        Returns
        -------
        int
            Aranan kullanıcının ID numarası.
        
        Raises
        ------
        KullaniciBulunamadi
            Aranan kullanıcı sistemde kayıtlı değil.
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.
        """
        
        try:
            with self.baglan() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                               SELECT kullanici_id
                               FROM kullanicilar
                               WHERE kullanici_adi=?
                               """, (kullanici_adi,))
                               
                result = cursor.fetchone()
                
                if result is None:
                    raise KullaniciBulunamadi("Kullanıcı bulunamadı")
                    
                return result[0]
        
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Kullanıcı ararken hata oluştu (database hatası).") from error
     
                    
    def kitap_bul(self, kullanici_id:int, isbn:str) -> tuple:
        """Aranan kitabın seçili kullanıcının kütüphanesinde olup olmadığını inceler ve
        bulunan kitabın bilgilerini döndürür.

        Parameters
        ----------
        kullanici_id : int
            Kullanıcı ID numarası.
        isbn : str
            Aranan kitabın ISBN'si.

        Raises
        ------
        KitapBulunamadi
            Aranan ISBN'ye sahip kitap belirtilen kullanıcının kütüphanesinde bulunamadı.
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.

        Returns
        -------
        tuple
            Belirtilen kullanıcıya ait, verilen ISBN numarasıyla eşleşen kitabı 
            (id, kullanici_id, baslik, yazar, isbn, tur, sayfa_sayisi, durum, bitis_tarihi) 
            sırasıyla içeren bir tuple olarak döndürür.

        """
         
        try:
            with self.baglan() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                               SELECT *
                               FROM kitaplar
                               WHERE kullanici_id=?
                               AND isbn=?""",
                               (kullanici_id, isbn))
                
                result = cursor.fetchone()
                if result is None:
                    raise KitapBulunamadi("Kitap bulunamadı")
                
                return result
            
        
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Kitap ararken hata oluştu (database hatası).") from error
            

    def kitap_sil(self, kullanici_id:int, isbn:str) -> None:
        """Belirltilen kitabı seçili kullanıcının kütüphanesinden siler.

        Parameters
        ----------
        kullanici_id : int
            Kullanıcı ID numarası.
        isbn : str
            Aranan kitabın ISBN'si.

        Raises
        ------
        KitapBulunamadi
            Aranan ISBN'ye sahip kitap belirtilen kullanıcının kütüphanesinde bulunamadı.
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.

        Returns
        -------
        None

        """

        try:
            with self.baglan() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                               DELETE FROM kitaplar
                               WHERE kullanici_id=?
                               AND isbn=?"""
                               ,(kullanici_id, isbn))
                
                if cursor.rowcount == 0:
                    raise KitapBulunamadi("Silinecek kitap bulunamadı.")
                    
                conn.commit()
               
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Kitap silinemedi") from error
             
            
    def kullanici_sil(self, kullanici_id:int) -> None:
        """Seçili kullanıcıyı sistemden siler.
        
        Parameters
        ----------
        kullanici_id : int
            Kullanıcı ID numarası.

        Raises
        ------
        KullaniciBulunamadi
            Aranan kullanıcı sistemde kayıtlı değil.
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.

        Returns
        -------
        None

        """
        try:
            with self.baglan() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                               DELETE FROM kullanicilar
                               WHERE kullanici_id=?"""
                               ,(kullanici_id,))
                
                if cursor.rowcount == 0:
                    raise KullaniciBulunamadi("Silinecek kullanıcı bulunamadı.")
                    
                conn.commit()
               
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Kullanıcı silinemedi") from error
         
    
    def kitaplari_listele(self, kullanici_id:int, tur:str | None = None, durum:str | None = None) -> list[tuple]:
        """Seçili kullanıcının kütüphanesindeki kitapları tür ve durum seçimiyle filtreleyerek listeler.
        
        Parameters
        ----------
        kullanici_id : int
            Kullanıcı ID numarası.
        tur : str | None, optional
            Kitaplar türüne göre listelenecek ise seçilen tür. The default is None.
        durum : str | None, optional
            Kitaplar okunma durumlarına göre listelenecek ise seçilen durum. The default is None.

        Raises
        ------
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.

        Returns
        -------
        list[tuple]
         Belirtilen kullanıcıya ait kitapları, isteğe bağlı tür ve durum filtrelerine göre, 
         her biri (id, baslik, yazar, isbn, tur, sayfa_sayisi, durum, bitis_tarihi) 
         sırasıyla içeren tuple'lardan oluşan bir liste olarak döndürür.

        """
        
        try:
            with self.baglan() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT id, baslik, yazar, isbn, tur, sayfa_sayisi, durum, bitis_tarihi
                FROM kitaplar
                WHERE kullanici_id=?"""
                
                params = [kullanici_id]
                
                if tur is not None:
                    query += " AND tur = ?"
                    params.append(tur)
                    
                if durum is not None:
                    query += " AND durum = ?"
                    params.append(durum)
                    
                cursor.execute(query, params)
                return cursor.fetchall()
            
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Kitaplar listelenemedi") from error


    def kitap_guncelle(self, isbn:str, kullanici_id:int, baslik:str | None = None, yazar:str | None = None, 
                       sayfa_sayisi:int | None = None, tur:str | None = None) -> None:
        """Belirtilen kitabın bilgilerini günceller (hatalı girme durumları için). ISBN güncellenemez.

        Parameters
        ----------
        isbn : str
            Bilgileri güncellenecek kitabın ISBN'si.
        kullanici_id : int
            Kullanıcı ID numarası.
        baslik : str | None, optional
            Güncelllenecek başlık bilgisi. The default is None.
        yazar : str | None, optional
            Güncelllenecek yazar bilgisi. The default is None.
        sayfa_sayisi : int | None, optional
            Güncelllenecek sayfa sayısı bilgisi. The default is None.
        tur : str | None, optional
            Güncelllenecek tür bilgisi. The default is None.

        Raises
        ------
        KitapBulunamadi
            Aranan ISBN'ye sahip kitap belirtilen kullanıcının kütüphanesinde bulunamadı.
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.

        Returns
        -------
        None

        """
        try:
            fields = []
            params = []
            
            if baslik is not None:
                fields.append("baslik = ?")
                params.append(baslik)
                
            if yazar is not None:
                fields.append("yazar = ?")
                params.append(yazar)
                
            if sayfa_sayisi is not None:
                fields.append("sayfa_sayisi=?")
                params.append(sayfa_sayisi)
                
            if tur is not None:
                fields.append("tur=?")
                params.append(tur)
            
            if not fields:
                return
            
            query = f"""
                UPDATE kitaplar
                SET  {", ".join(fields)}
                WHERE kullanici_id = ?
                AND isbn = ?"""
            
            params.extend([kullanici_id, isbn])      
            
            with self.baglan() as conn:
                cursor = conn.cursor()
                cursor.execute(query,params)
                
                if cursor.rowcount == 0:
                    raise KitapBulunamadi("Güncellenecek kitap bulunamadı")
                
                conn.commit()
        
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Kitap güncellenemedi") from error


    def durum_guncelle(self, isbn:str, kullanici_id:int, durum:str) -> None:
        """Seçilen kitabın durumunu kullanıcının kütüphanesinde günceller.

        Parameters
        ----------
        isbn : str
            Durumu güncellenecek kitabın ISBN'si.
        kullanici_id : int
            Kullanıcı ID numarası.
        durum : str
            Güncellenecek olan durum (yeni durum).

        Raises
        ------
        KitapBulunamadi
            Aranan ISBN'ye sahip kitap belirtilen kullanıcının kütüphanesinde bulunamadı.
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.

        Returns
        -------
        None

        """
        try:
            if durum == "okundu":
                bitis_tarihi = date.today().isoformat()
            else:
                bitis_tarihi=None  
            
            with self.baglan() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                        UPDATE kitaplar
                        SET durum =?,
                            bitis_tarihi=?
                        WHERE kullanici_id=?
                        AND isbn=?"""
                        ,(durum,bitis_tarihi,kullanici_id,isbn))
                
                if cursor.rowcount == 0:
                    raise KitapBulunamadi("Durumu güncellenecek kitap bulunamadı.")
                
                conn.commit()
        
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Durum güncellenemedi") from error
            
      
    def not_ekle(self, isbn:str, kullanici_id:int, not_metni:str, sayfa:int| None = None) -> None:
        """ Kullanıcının kütüphanesinden seçilen kitaba not ekler.

        Parameters
        ----------
        isbn : str
            Not eklenecek kitabın ISBN'si.
        kullanici_id : int
            Kullanıcı ID numarası.
        not_metni : str
            Eklenecek olan not metni.
        sayfa : int| None, optional
            Not eklenecek olan sayfa numarası. The default is None.

        Raises
        ------
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.

        Returns
        -------
        None

        """
        try:
            kitap = self.kitap_bul(kullanici_id, isbn)
            kitap_id = kitap[0]   #id is the first component of the kitaplar table (assigned in line 38)
            
            with self.baglan() as conn:
                cursor = conn.cursor()
                
                #not eklenen kitabın durumu okunacak ise, not eklendiğinde durum okunuyor olarak değişiyor
                cursor.execute("""
                            UPDATE kitaplar
                            SET durum = 'okunuyor'
                            WHERE id = ?
                              AND durum = 'okunacak'
                              """, (kitap_id,))

                cursor.execute("""
                               INSERT INTO notlar(
                                   kitap_id, not_metni, sayfa)
                               VALUES (?,?,?)""",
                               (kitap_id, not_metni,sayfa))
                conn.commit()
                
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Not eklenemedi.") from error
            
      
    def notlari_listele(self, isbn:str, kullanici_id:int) -> list[tuple]:
        """ Kullanıcıya kayıtlı olan seçili kitaptaki tüm notları listeler.

        Parameters
        ----------
        isbn : str
            Notları listelenecek olan kitabın ISBN'si.
        kullanici_id : int
            Kullanıcı ID numarası.

        Raises
        ------
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.

        Returns
        -------
        list[tuple]
            Belirtilen kitaba ait tüm notları, her biri 
            (not_id, kitap_id, not_metni, sayfa) sırasıyla içeren 
            tuple'lardan oluşan bir liste olarak döndürür.

        """
        try:
            kitap = self.kitap_bul(kullanici_id, isbn)
            kitap_id = kitap[0]
            
            with self.baglan() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                               SELECT *
                               FROM notlar
                               WHERE kitap_id =?""",
                               (kitap_id,))
                
                return cursor.fetchall()
                
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Notlar bulunamadı.") from error
            
            
    def tum_notlari_listele(self, kullanici_id:int) -> list[tuple]:
        """Belirtilen kullanıcıya ait tüm notları listeler.

        Parameters
        ----------
        kullanici_id : int
            Kullanıcı ID numarası.

        Raises
        ------
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.

        Returns
        -------
        list[tuple]
            Belirtilen kullanıcıya ait tüm notları, her biri 
            (not_id, baslik, isbn, not_metni, sayfa) sırasıyla içeren 
            tuple'lardan oluşan bir liste olarak döndürür.

        """
        try:
            with self.baglan() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                        SELECT notlar.not_id,
                               kitaplar.baslik,
                               kitaplar.isbn,
                               notlar.not_metni,
                               notlar.sayfa
                        FROM notlar
                               INNER JOIN kitaplar
                               ON notlar.kitap_id = kitaplar.id
                               WHERE kitaplar.kullanici_id=?
                               ORDER BY kitaplar.baslik, notlar.sayfa""", (kullanici_id,))
                               
                return cursor.fetchall()
            
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Kullanıcı notları listelenemedi.") from error
            
            
      
    def kitap_ara(self, kullanici_id: int, anahtar_kelime:str) -> list[tuple]:
        """Verilen anahtar kelimenin kullanıcının kütüphanesindeki kitapların 
        yazar veya başlıklarında bulunmasını inceler. 
        Bulunan kitabın bilgilerini liste olarak döndürür.

        Parameters
        ----------
        kullanici_id : int
            Kullanıcı ID numarası.
        anahtar_kelime : str
            Aramada kullanılacak olan anahtar kelime 
            (kitabın bulunabilmesi için başlık veya yazarın bir parçası olmalı).

        Raises
        ------
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.

        Returns
        -------
        list[tuple]
            Belirtilen kullanıcıya ait kitaplar arasında başlık veya yazar 
            alanında verilen anahtar kelimeyi içerenleri, her biri 
            (id, kullanici_id, baslik, yazar, isbn, tur, sayfa_sayisi, durum, bitis_tarihi) 
            sırasıyla içeren tuple'lardan oluşan bir liste olarak döndürür.

        """
        try:
            with self.baglan() as conn:
                cursor = conn.cursor()
                
                arama = f"%{anahtar_kelime}%"
                
                cursor.execute("""
                               SELECT *
                               FROM kitaplar
                               WHERE kullanici_id=?
                               AND(baslik LIKE ? 
                                   OR yazar LIKE ?)""",
                               (kullanici_id, arama, arama))
                
                return cursor.fetchall()
            
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Kitap arama başarısız") from error
            
     
    def tur_dagilimi(self, kullanici_id:int) -> list[tuple]:
        """Belirtilen kullanıcının kütüphanesindeki kitapları

        Parameters
        ----------
        kullanici_id : int
            Kullanıcı ID numarası.

        Raises
        ------
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.

        Returns
        -------
        list[tuple]
            Belirtilen kullanıcıya ait kitapları türlerine göre gruplandırıp, her biri 
            (tur, kitap_sayisi) sırasıyla içeren tuple'lardan oluşan bir liste olarak döndürür.

        """
        try:
            with self.baglan() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                               SELECT tur, COUNT(*) as kitap_sayisi
                               FROM kitaplar
                               WHERE kullanici_id=?
                               GROUP BY tur""", (kullanici_id,))
                
                return cursor.fetchall()
            
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Tür dağılımı algılanamadı") from error
                     
    
    def ozet_bilgisi(self, kullanici_id:int) -> tuple:
        """Belirtilen kullanıcının kütüphanesindeki toplam kitap sayısı, okunmuş kitap sayısı, 
        okunmuş kitapların toplam sayfa sayısı bilgilerini döndürür.

        Parameters
        ----------
        kullanici_id : int
            Kullanıcı ID numarası.

        Raises
        ------
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.

        Returns
        -------
        tuple
            Belirtilen kullanıcıya ait toplam kitap sayısı, okunan kitap sayısı 
            ve okunan kitapların toplam sayfa sayısını (toplam_kitap, okunan_kitap, toplam_sayfa) 
            sırasıyla içeren bir tuple olarak döndürür.

        """
        try:
            with self.baglan() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT
                        COUNT(*) AS toplam_kitap,
                        SUM(CASE WHEN durum = 'okundu' THEN 1 ELSE 0 END) AS okunan_kitap,
                        SUM(CASE WHEN durum = 'okundu' THEN sayfa_sayisi ELSE 0 END) AS toplam_sayfa
                    FROM kitaplar
                    WHERE kullanici_id = ?""", (kullanici_id,))
    
                return cursor.fetchone()
    
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Özet bilgisi alınamadı.") from error
            
               
    def okunan_kitaplari_getir(self, kullanici_id:int) -> list[tuple]:
        """Belirtilen kullanıcının okumuş olduğu kitapların bilgilerini döndurur.

        Parameters
        ----------
        kullanici_id : int
            Kullanıcı ID numarası.

        Raises
        ------
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.

        Returns
        -------
        list[tuple]
            Belirtilen kullanıcıya ait durumu 'okundu' olan kitapları, her biri 
            (baslik, yazar, isbn, tur, sayfa_sayisi, bitis_tarihi) sırasıyla içeren 
            tuple'lardan oluşan bir liste olarak döndürür.

        """
        try:
            with self.baglan() as conn:
                cursor = conn.cursor()
    
                cursor.execute("""
                    SELECT baslik, yazar, isbn, tur, sayfa_sayisi, bitis_tarihi
                    FROM kitaplar
                    WHERE kullanici_id = ?
                      AND durum = 'okundu' """, (kullanici_id,))
    
                return cursor.fetchall()
    
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Okunan kitaplar alınamadı.") from error
            
        
    def sifirla(self) -> None:
        """Veritabanındaki tüm bilgileri sıfırlar.
        
        Raises
        ------
        VeritabaniHatasi
            Veritabanında bir hata yaşandı.

        Returns
        -------
        None

        """
        try:
            with self.baglan() as conn:
                cursor = conn.cursor()
    
                cursor.execute("DELETE FROM notlar")
                cursor.execute("DELETE FROM kitaplar")
                cursor.execute("DELETE FROM kullanicilar")
    
                conn.commit()

        except sqlite3.Error as error:
            raise VeritabaniHatasi("Veritabanı sıfırlanamadı") from error
            

    
    def okuma_sinyali_verisi(self, kullanici_id: int) -> list[tuple]:
        """Kullanıcının okuma alışkanlıklarını göstermek üzere kitapların tamamlandıkları gün 
        ve uzunluklarının gösterildiği bir grafik oluşturur.

        Parameters
        ----------
        kullanici_id : int
            İncelenen kullanıcının ID numarası.

        Raises
        ------
        VeritabaniHatasi
            Okuma sinyali verisi veritabanında bulunamazsa.

        Returns
        -------
        list[tuple]
        """
        try: 
            with self.baglan() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                               SELECT bitis_tarihi, SUM(sayfa_sayisi)
                               FROM kitaplar
                               WHERE kullanici_id = ?
                                   AND durum = 'okundu'
                                   AND bitis_tarihi IS NOT NULL
                                 GROUP BY bitis_tarihi
                                 ORDER BY bitis_tarihi""",(kullanici_id,))
                                 
                return cursor.fetchall()
            
        except sqlite3.Error as error:
            raise VeritabaniHatasi("Okuma sinyali verisi alınamadı") from error
            
            
            
    def kullanicilari_listele(self) -> list[tuple]:
        """Sistemdeki tüm kullanıcıları listeler.

        Returns
        -------
        list[tuple]
            Sisteme kayıtlı kullanıcıları liste olarak döndürür.

        """
        
        try:
            with self.baglan() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                               SELECT kullanici_id, kullanici_adi
                               FROM kullanicilar
                               ORDER BY kullanici_id""")
                return cursor.fetchall()
        
        except sqlite3.Error as error:
            raise KullaniciBulunamadi("Kullanıcılar listelenemedi") from error
            