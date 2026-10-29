"""
CLI commands can be written here using argparse
"""

import argparse
import sys
import logging

from src.database import VeritabaniYoneticisi
from src.library import Kutuphane
from src.exceptions import LibroTrackHatasi
from src.config import load_config  
from src.test_additions import stress_test, benchmark, monte_carlo_test


def setup_logging(config: dict) -> None:
    logger_root = logging.getLogger()
    logger_root.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

    #console is info and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config["logging"]["console_level"]))
    console_handler.setFormatter(formatter)

    #log file is debug and above
    file_handler = logging.FileHandler(
        config["logging"]["file"],
        encoding="utf-8")
    file_handler.setLevel(getattr(logging, config["logging"]["file_level"]))
    file_handler.setFormatter(formatter)

    logger_root.handlers.clear()
    logger_root.addHandler(console_handler)
    logger_root.addHandler(file_handler)
#The logging format is: current date and time, logging level name, logger file name, message
#Logged to the file: librotrack.log


def main() -> int:
    config = load_config()
    setup_logging(config)
    db = VeritabaniYoneticisi(config["database"]["path"])
    kutuphane = Kutuphane(db)
    
    parser = argparse.ArgumentParser(description = "Librotrack")
    subparsers = parser.add_subparsers(dest="komut", required=True)
    
    #---kullanıcı ekle
    kullanici_ekle_parser = subparsers.add_parser("kullanici-ekle")
    kullanici_ekle_parser.add_argument("--kullanici", required = True)
    
    #--kitap ekle
    kitap_ekle_parser = subparsers.add_parser("kitap-ekle")
    kitap_ekle_parser.add_argument("--kullanici", required=True)
    kitap_ekle_parser.add_argument("--baslik", required=True)
    kitap_ekle_parser.add_argument("--yazar", required=True)
    kitap_ekle_parser.add_argument("--isbn", required=True)
    kitap_ekle_parser.add_argument("--tur", required=True)
    kitap_ekle_parser.add_argument("--sayfa-sayisi", required=True, type=int)
    
    #--kitap sil
    kitap_sil_parser = subparsers.add_parser("kitap-sil")
    kitap_sil_parser.add_argument("--kullanici", required = True)
    kitap_sil_parser.add_argument("--isbn", required = True)
    
    #--kullanıcı sil
    kullanici_sil_parser = subparsers.add_parser("kullanici-sil")
    kullanici_sil_parser.add_argument("--kullanici", required = True)
    
    #--kitapları listele
    kitap_listele_parser = subparsers.add_parser("kitap-listele")
    kitap_listele_parser.add_argument("--kullanici", required=True)
    kitap_listele_parser.add_argument("--tur")
    kitap_listele_parser.add_argument("--durum")
    
    #--durum güncelle
    durum_parser = subparsers.add_parser("durum-guncelle")
    durum_parser.add_argument("--kullanici", required = True)
    durum_parser.add_argument("--isbn", required = True)
    durum_parser.add_argument("--durum", required = True)
    
    #--kitap bilgilerini güncelle
    kitap_guncelle_parser = subparsers.add_parser("kitap-guncelle")
    kitap_guncelle_parser.add_argument("--kullanici", required = True)
    kitap_guncelle_parser.add_argument("--isbn", required = True)
    kitap_guncelle_parser.add_argument("--baslik")
    kitap_guncelle_parser.add_argument("--yazar")
    kitap_guncelle_parser.add_argument("--tur")
    kitap_guncelle_parser.add_argument("--sayfa-sayisi", type=int)
    
    #--not ekle
    not_ekle_parser = subparsers.add_parser("not-ekle")
    not_ekle_parser.add_argument("--kullanici", required=True)
    not_ekle_parser.add_argument("--isbn", required=True)
    not_ekle_parser.add_argument("--not-metni", required=True)
    not_ekle_parser.add_argument("--sayfa", type = int)
    
    #--bir kitaptaki notları listele
    not_listele_parser = subparsers.add_parser("notlari-listele")
    not_listele_parser.add_argument("--kullanici", required=True)
    not_listele_parser.add_argument("--isbn", required=True)
    
    #--kitap ara
    kitap_ara_parser = subparsers.add_parser("kitap-ara")
    kitap_ara_parser.add_argument("--kullanici", required=True)
    kitap_ara_parser.add_argument("--anahtar-kelime", required=True)
    
    #--tür dağılım grafiği oluşturma
    tur_dagilimi_parser = subparsers.add_parser("tur-dagilimi")
    tur_dagilimi_parser.add_argument("--kullanici", required=True)
    tur_dagilimi_parser.add_argument("--dosya", default="tur_dagilimi.png")
    
    #--özet (toplam kitap sayısı, okunan kitap sayısı, okunan sayfa sayısı)
    ozet_parser = subparsers.add_parser("ozet")
    ozet_parser.add_argument("--kullanici", required=True)
       
    #--csv dosyası oluşturma
    csv_parser = subparsers.add_parser("csv-aktar")
    csv_parser.add_argument("--kullanici", required=True)
    csv_parser.add_argument("--dosya", default="okunan_kitaplar.csv")
     
    #--sistemi sıfırlama (girilen tüm verileri silme)
    sifirla_parser=subparsers.add_parser("sifirla")
    
    #--stress test
    stress_parser = subparsers.add_parser("stress-test")
    stress_parser.add_argument("--kullanici-sayisi", type=int, default=50)
    stress_parser.add_argument("--kitap-sayisi", type=int, default=20)
    
    #--benchmark
    benchmark_parser = subparsers.add_parser("benchmark")
    benchmark_parser.add_argument("--kitap-sayilari", nargs="+", type=int, default=[100,500,1000])
    benchmark_parser.add_argument("--csv", default="benchmark_sonuclari.csv")
    benchmark_parser.add_argument("--grafik", default="benchmark.png")
    
    #--monte carlo testing
    monte_carlo_parser = subparsers.add_parser("monte-carlo")
    monte_carlo_parser.add_argument("--runs", type=int, default=20)
    monte_carlo_parser.add_argument(("--max-users"), type=int, default=10)
    monte_carlo_parser.add_argument(("--max-books"), type=int, default=20)

    #--okuma verisi sinyal grafiği
    reading_signal_parser = subparsers.add_parser("reading-signal")
    reading_signal_parser.add_argument("--kullanici", required=True)
    reading_signal_parser.add_argument("--dosya", default="reading_signal.png")
    
    
    #--kayıtlı kullanıcıları listeleme
    subparsers.add_parser("kullanici-listele")
    
    #--kullanıcının tüm notlarını listeleme
    tum_notlar_parser = subparsers.add_parser("tum-notlari-listele")
    tum_notlar_parser.add_argument("--kullanici", required=True)
    
    args = parser.parse_args()
        
    try:
        if args.komut == "kullanici-ekle":
            kutuphane.kullanici_ekle(args.kullanici)
            print("Kullanıcı eklendi.")
            
        elif args.komut == "kitap-ekle":
            kutuphane.kitap_ekle(kullanici_adi=args.kullanici,
                                 baslik=args.baslik, 
                                 yazar=args.yazar, 
                                 isbn=args.isbn, 
                                 tur=args.tur, 
                                 sayfa_sayisi=args.sayfa_sayisi)
            print("Kitap eklendi")
        
        elif args.komut == "kitap-sil":
            kutuphane.kitap_sil(kullanici_adi=args.kullanici, isbn=args.isbn)
            print("Kitap silindi")
        
        elif args.komut == "kullanici-sil":
            kutuphane.kullanici_sil(kullanici_adi=args.kullanici)
            print("Kullanici silindi")
        
        elif args.komut =="kitap-listele":
            kitaplar = kutuphane.kitaplari_listele(kullanici_adi=args.kullanici, tur=args.tur, durum=args.durum)
            if not kitaplar:
                print("Hiç kitap bulunamadı")
            else:
                for kitap in kitaplar:
                    print(f"""
                        Başlık        : {kitap[1]}
                        Yazar         : {kitap[2]}
                        ISBN          : {kitap[3]}
                        Tür           : {kitap[4]}
                        Sayfa Sayısı  : {kitap[5]}
                        Durum         : {kitap[6]}
                        Bitiş Tarihi  : {kitap[7]}
                        ------------------------------
        """)
        
        elif args.komut == "kitap-guncelle":
            kutuphane.kitap_guncelle(kullanici_adi=args.kullanici, isbn=args.isbn, baslik=args.baslik,
                                     yazar=args.yazar, tur=args.tur, sayfa_sayisi=args.sayfa_sayisi)
            print("Kitap güncellendi")
            
        elif args.komut == "durum-guncelle":
            kutuphane.durum_guncelle(kullanici_adi=args.kullanici, isbn=args.isbn, yeni_durum=args.durum)
            print("Durum güncellendi")
            
        elif args.komut =="not-ekle":
            kutuphane.not_ekle(kullanici_adi=args.kullanici, isbn=args.isbn, 
                               not_metni=args.not_metni, not_sayfasi=args.sayfa)
            print("Not eklendi")
            
        elif args.komut == "notlari-listele":
            notlar = kutuphane.notlari_listele(kullanici_adi=args.kullanici, isbn=args.isbn)
            if not notlar:
                print("Bu kitapta not bulunamadı")
            else:
                for not_kaydi in notlar:
                    print(f"""
                          Not ID      : {not_kaydi[0]}
                          Kitap ID    : {not_kaydi[1]}
                          Sayfa       : {not_kaydi[3]}
                          Not         : {not_kaydi[2]}
                          ------------------------------
                          """)
                          
        elif args.komut == "tum-notlari-listele":
            notlar = kutuphane.tum_notlari_listele(kullanici_adi= args.kullanici)
            if not notlar:
                print("Kullanıcının kayıtlı notu bulunamadı")
                
            else:
                for not_kaydi in notlar:
                    print(f"""
                            Kitap       : {not_kaydi[1]}
                            ISBN        : {not_kaydi[2]}
                            Sayfa       : {not_kaydi[4]}
                            Not         : {not_kaydi[3]}
                            Not ID      : {not_kaydi[0]}
                            ------------------------------
                            """)        
        
        elif args.komut == "kitap-ara":
            kitaplar = kutuphane.kitap_ara(kullanici_adi=args.kullanici, anahtar_kelime=args.anahtar_kelime)
            if not kitaplar:
                print("Aranan kitap bulunamadı")
            else:
                for kitap in kitaplar:
                    print(f"""
                            Başlık        : {kitap[1]}
                            Yazar         : {kitap[2]}
                            ISBN          : {kitap[3]}
                            Tür           : {kitap[4]}
                            Sayfa Sayısı  : {kitap[5]}
                            Durum         : {kitap[6]}
                            Bitiş Tarihi  : {kitap[7]}
                            ------------------------------
                            """)  
                            
        elif args.komut == "tur-dagilimi":
            kutuphane.tur_dagilimi_grafigi(kullanici_adi=args.kullanici, dosya_adi=args.dosya)
            print(f"Tür dağılımı grafiği kaydedildi: {args.dosya}")
        
        elif args.komut == "ozet":
            toplam_kitap, okunan_kitap, toplam_sayfa = kutuphane.ozet_goster(kullanici_adi=args.kullanici)
            print(f"""
                Toplam Kitap Sayısı        : {toplam_kitap}
                Okunan Kitap Sayısı        : {okunan_kitap}
                Tamamlanan Toplam Sayfa    : {toplam_sayfa}
                """)
            
        elif args.komut == "csv-aktar":
            kutuphane.okunan_kitaplari_csv_aktar(kullanici_adi=args.kullanici, dosya_adi=args.dosya)
            print(f"CSV dosyası oluşturuldu: {args.dosya}")
    
        elif args.komut == "sifirla":
            #sistem sıfırlanmadan önce kontrol için çifte kontrol yapılır.
            cevap = input("Sistemin sıfırlanmasını onaylıyor musunuz? (evet/hayır)")
            
            if cevap == "evet":
                kutuphane.sifirla()
                print("Veritabanı sıfırlandı")
            else:
                print("Sıfırlama işlemi gerçekleşmedi")
           
        elif args.komut == "stress-test":
            sonuc = stress_test(kullanici_sayisi=args.kullanici_sayisi, kullanici_basina_kitap=args.kitap_sayisi)
            print(f"""
            Stress Test Tamamlandı
            ----------------------
            Kullanıcı Sayısı        : {sonuc["kullanici_sayisi"]}
            Kullanıcı Başına Kitap  : {sonuc["kullanici_basina_kitap"]}
            Toplam Kitap            : {sonuc["toplam_kitap"]}
            Hata Sayısı             : {sonuc["hata_sayisi"]}
            Geçen Süre              : {sonuc["gecen_sure"]:.4f} saniye
            Test Veritabanı         : {sonuc["db_path"]}
            """)
        
        elif args.komut ==  "benchmark":
            sonuc = benchmark(kitap_sayilari=args.kitap_sayilari, csv_path=args.csv, graph_path=args.grafik)
            print("Benchmark tamamlandı.")
            print(f"CSV kaydedildi: {sonuc['csv']}")
            print(f"Grafik kaydedildi: {sonuc['grafik']}")
            
            for s in sonuc["sonuclar"]:
                print(f"  {s['kitap_sayisi']} kitap: {s['sure_saniye']}s ({s['kitap_basina_ms']}ms/kitap)")  
        
        elif args.komut == "monte-carlo":
            sonuc = monte_carlo_test(runs=args.runs, max_users=args.max_users, max_books_per_user=args.max_books)
            print(f"""
                  Monte Carlo Test Tamamlandı
                  Run Sayısı : {sonuc["runs"]}
                  Ortalama Kitap : {sonuc["ortalama_kitap"]:.2f}
                  Ortalama Süre : {sonuc["ortalama_sure"]:.4f} saniye
                  Ortalama Hata : {sonuc["ortalama_hata"]:.2f}
                  Minimum Kitap : {sonuc["minimum_kitap"]}
                  Maksimum Kitap : {sonuc["maksimum_kitap"]}
                  """)
         
        elif args.komut == "reading-signal":
            kutuphane.okuma_sinyali_grafigi(kullanici_adi=args.kullanici, dosya_adi=args.dosya)
            print(f"Okuma sinyali grafiği kaydedildi: {args.dosya}")
        
        elif args.komut == "kullanici-listele":
            kullanicilar = kutuphane.kullanicilari_listele()
            if not kullanicilar:
                print("Sistemde kayıtlı kullanıcı bulunamadı.")
            else:
                print(f"{'ID':<6} {'Kullanıcı Adı'}")
                print("-" * 30)
                for k in kullanicilar:
                    print(f"{k[0]:<6} {k[1]}")
        
        
        return 0
    
    except LibroTrackHatasi as error:
        print(f"Hata:{error}")
        return 1
    
        
    
if __name__ == "__main__":
    sys.exit(main())