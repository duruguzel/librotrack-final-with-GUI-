"""
-stress test (high number of users and books), 
-benchmark (with csv and graph) (shows the capacity of the system to adding an increasing number of books), 
-monte carlo testing  (many random scenarios)

"""

import os
import time
import logging
import csv
import matplotlib.pyplot as plt
import random

from src.database import VeritabaniYoneticisi
from src.library import Kutuphane
from contextlib import contextmanager


@contextmanager   #turns a generator func to sth you can use with "with"
#suppresses logging during the test and retores it afterwards
def logging_sustur(level: int = logging.WARNING):
    """Stres testi sıraısnda INFO logging durdurulur"""
    root_logger = logging.getLogger()
    eski_seviye = root_logger.level
    root_logger.setLevel(level)
    
    try:
        yield
    finally:
        root_logger.setLevel(eski_seviye)


def stress_test(kullanici_sayisi: int=50, kullanici_basina_kitap: int=20, 
                db_path: str="stress_test.db") -> dict:
    """Sistemin fazla kullanıcı ve kitap ile çökmediğini kontrol etmek için stres testi

    Parameters
    ----------
    kullanici_sayisi : int, optional
        Sisteme eklenecek kullanıcı sayısı. The default is 50.
    kullanici_basina_kitap : int, optional
        Her bir kullanıcı için eklenecek olan kitap sayısı. The default is 20.
    db_path : str, optional
        Stres testi için olutşurulan veritabanının dosya adı. The default is "stress_test.db".

    Returns
    -------
    dict
        "kullanıcı sayısı, kullanıcı başına eklenen kitap sayısı, toplam kitap, geçen süre, 
        sisteme bilgiler eklenirken oluşan toplam hata sayısı, sisteme bilgiler eklenirken
        geçen süre, oluşturulan veritabanının adı" bilgilerini içerir.

    """
    
    if os.path.exists(db_path):  #each stress test starts with a clean database
        os.remove(db_path)
        
    db = VeritabaniYoneticisi(db_path)
    #stress test uses a separate database, it doesn't change the actual user/book data in librotrack.db
    kutuphane = Kutuphane(db)
    
    baslangic = time.perf_counter()
    
    hata_sayisi = 0
    toplam_kitap = 0
    
    with logging_sustur(logging.WARNING):
        for kullanici_index in range(kullanici_sayisi):
            kullanici_adi = f"stress_user_{kullanici_index}"
            
            try:
                kutuphane.kullanici_ekle(kullanici_adi)
                
                for kitap_index in range(kullanici_basina_kitap):
                    isbn = f"{kullanici_index}-{kitap_index}"
                    
                    kutuphane.kitap_ekle(
                        kullanici_adi = kullanici_adi,
                        baslik = f"Book {kitap_index}",
                        yazar = f"Author {kitap_index}",
                        isbn = isbn,
                        tur = "test",
                        sayfa_sayisi = 100 + kitap_index 
                    )
                    
                    toplam_kitap += 1
                    
            except Exception:
                hata_sayisi += 1
                     
    bitis = time.perf_counter()
    gecen_sure = bitis - baslangic
    
    logging.getLogger(__name__).info(
        "Stress test completed: %s users, %s books, %.4f seconds",
        kullanici_sayisi,
        toplam_kitap,
        gecen_sure)
    
    return{
        "kullanici_sayisi": kullanici_sayisi,
        "kullanici_basina_kitap": kullanici_basina_kitap,
        "toplam_kitap": toplam_kitap,
        "hata_sayisi": hata_sayisi,
        "gecen_sure": gecen_sure,
        "db_path": db_path}



def benchmark(
        kitap_sayilari: list[int]=[100,500,1000],
        db_path: str = "benchmark.db",
        csv_path: str = "benchmark.csv",
        graph_path: str = "benchmark.png") -> dict:
    """ Her kitap sayısı için ekleme süresini ölçer ve performansı kıyaslar. 
    Sonuçları CSV ve grafik olarak kaydeder.

    Parameters
    ----------
    kitap_sayilari : list[int], optional
        Sistem hızı incelenecek kitap sayıları. The default is [100,500,1000].
    db_path : str, optional
        Oluşturulacak veritabanının adı. The default is "benchmark.db".
    csv_path : str, optional
        Oluşturulacak CSV dosyasının adı. The default is "benchmark.csv".
    graph_path : str, optional
        Oluşturulacak grafik dosyasının adı. The default is "benchmark.png".

    Returns
    -------
    dict
        "kitap sayısı, işlem süresi, kitap başına geçen süre (ms), 
        csv dosyası, garfik dosyası" bilgilerini içerir.

    """
    sonuclar = []
    
    for kitap_sayisi in kitap_sayilari:
        current_db_path = f"benchmark_{kitap_sayisi}.db"
    
        if os.path.exists(current_db_path):
            os.remove(current_db_path)
    
        db = VeritabaniYoneticisi(current_db_path)
        kutuphane = Kutuphane(db)
        
        with logging_sustur(logging.WARNING):
            kutuphane.kullanici_ekle("benchmark_user")
            
            baslangic = time.perf_counter()
            
            for i in range(kitap_sayisi):
                kutuphane.kitap_ekle(
                    kullanici_adi="benchmark_user",
                    baslik=f"Kitap {i}",
                    yazar=f"Yazar {i}",
                    isbn=str(i),
                    tur="test",
                    sayfa_sayisi=100)
                
            bitis = time.perf_counter()
            gecen_sure = bitis - baslangic
                
        sonuclar.append({
            "kitap_sayisi": kitap_sayisi,
            "sure_saniye": round(gecen_sure, 4),
            "kitap_basina_ms": round((gecen_sure / kitap_sayisi) * 1000, 4)})
        print(f"{kitap_sayisi} kitap: {gecen_sure:.4f}s ({(gecen_sure/kitap_sayisi)*1000:.4f}ms/kitap)")
        
        
    #--csv
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["kitap_sayisi", "sure_saniye", "kitap_basina_ms"])
        writer.writeheader()
        writer.writerows(sonuclar)
        
    #--graph
    kitap_axis = [s["kitap_sayisi"] for s in sonuclar]
    sure_axis = [s["sure_saniye"] for s in sonuclar]
    
    plt.figure()
    plt.plot(kitap_axis, sure_axis, marker = "o")
    plt.xlabel("kitap sayısı")
    plt.ylabel("süre (saniye)")
    plt.title("Sistemin Kitap ve Kullanıcı Ekleme Performansı")
    plt.grid(True)
    plt.savefig(graph_path)
    plt.close()
          
    return {"sonuclar": sonuclar, "csv": csv_path, "grafik": graph_path}
        



def monte_carlo_test(runs: int=20, max_users: int=10, max_books_per_user: int=20) -> dict:
    """Randomize edilmiş testler yapıp ortalamayı inceler.

    Parameters
    ----------
    runs : int, optional
        Sistemin çalıştırılma sayısı. The default is 20.
    max_users : int, optional
        Seçilebilecek maksimum kullanıcı sayısı. The default is 10.
    max_books_per_user : int, optional
        Her bir kullanıcı için seçilebilecek maksimum kitap sayısı. The default is 20.

    Returns
    -------
    dict
        Sistemin performansını gösteren istatistiksel özet bilgileri döndürür 
        (runs, ortalama kitap,  ortalama süre, ortalama hata, maksimum kitap, minimum kitap).

    """
    toplam_kitaplar = []
    toplam_sureler = []
    toplam_hatalar = []
    
    for i in range(runs):
        kullanici_sayisi = random.randint(1, max_users)
        kitap_sayisi = random.randint(1, max_books_per_user)
        sonuc = stress_test(kullanici_sayisi=kullanici_sayisi, 
                            kullanici_basina_kitap=kitap_sayisi, 
                            db_path=f"monte_carlo_{i}.db")
        
        toplam_kitaplar.append(sonuc["toplam_kitap"])
        toplam_sureler.append(sonuc["gecen_sure"])
        toplam_hatalar.append(sonuc["hata_sayisi"])
        
    return {
        "runs": runs,
        "ortalama_kitap": sum(toplam_kitaplar) / runs,
        "ortalama_sure": sum(toplam_sureler) / runs,
        "ortalama_hata": sum(toplam_hatalar) / runs,
        "maksimum_kitap": max(toplam_kitaplar),
        "minimum_kitap": min(toplam_kitaplar)}
        
