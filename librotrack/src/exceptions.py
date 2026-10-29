"""
custom error classes
"""

class LibroTrackHatasi(Exception):
    pass
#Tüm hatalar

class VeritabaniHatasi(LibroTrackHatasi):
    pass
#Database hataları (SQL)

class KitapBulunamadi(LibroTrackHatasi):
    pass
#Girilen isbn ile kayıtlı kitap yok

class KullaniciBulunamadi(LibroTrackHatasi):
    pass
#Girilen ad ile kayıtlı kullanıcı yok

class ISBN_mevcut(LibroTrackHatasi):
    pass
#Girilen isbn seçili kullanıcıda zaten kayıtlı

class kullanici_mevcut(LibroTrackHatasi):
    pass
#Girilen kullanıcı adı zaten sistemde kayıtlı

class hatali_bilgi(LibroTrackHatasi):
    pass
#Girilen bilgilerde tutarsızlık var(negatif sayfa vb)
