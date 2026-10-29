import tkinter as tk
from tkinter import ttk, messagebox

from src.config import load_config
from src.database import VeritabaniYoneticisi
from src.library import Kutuphane
from src.exceptions import kullanici_mevcut, KullaniciBulunamadi, LibroTrackHatasi


config = load_config()
db = VeritabaniYoneticisi(config["database"]["path"])
kutuphane = Kutuphane(db)

class Intro(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.title("LibroTrack - Kullanıcı Girişi")
        self.geometry("500x350")
        
        tk.Label(self, text="LibroTrack", font=("Times New Roman", 20, "bold")).pack(pady=20)
        tk.Label(self, text="Kullanıcı seçin veya kullanıcı ekleyin", 
                 font=("Times New Roman", 15)).pack(pady=5)
        
        self.user_status = tk.IntVar(value=1)  # default selection

        def select(choice):
            self.user_status.set(choice)
            # update button appearance to show selection
            if choice == 1:
                btn1.config(relief=tk.SUNKEN, bg="lightblue")
                btn2.config(relief=tk.RAISED, bg="SystemButtonFace")
            else:
                btn2.config(relief=tk.SUNKEN, bg="lightblue")
                btn1.config(relief=tk.RAISED, bg="SystemButtonFace")
        
        btn1 = tk.Button(self, text="Kayıtlı kullanıcı girişi",
                         width=25, font=("Times New Roman", 13),
                         command=lambda: select(1))
        btn1.pack(padx=40, pady=5)
        
        btn2 = tk.Button(self, text="Yeni kullanıcı kaydı",
                         width=25, font=("Times New Roman", 13),
                         command=lambda: select(2))
        btn2.pack(padx=40, pady=5)
        
        tk.Button(self, text="Enter",
                  width=10,
                  command=self.cont).pack(pady=10)
        
        
    def cont(self):
        user_choice = self.user_status.get()
        if user_choice == 1:
            self.withdraw()
            Login(self)
            
        elif user_choice == 2:
            self.withdraw()
            NewUser(self)
            


class NewUser(tk.Toplevel):
    
    def __init__(self, intro: Intro):
        super().__init__(intro)
        self.intro = intro 
        
        self.title("Yeni Kullanıcı Kaydı")
        self.geometry("400x350")
        
        #if the user manually closes the window, the system goes back to login (intro)
        self.protocol("WM_DELETE_WINDOW", self.back)
        
        tk.Label(self, text="Yeni Kullanıcı Kaydı",
                 font=("Times New Roman", 15, "bold")).pack(pady=10)
        
        form = tk.Frame(self)
        form.pack(padx=30)
        
        
        #--username
        tk.Label(form, text="Kullanıcı Adı:",
                font=("Times New Roman", 13), anchor="w").grid(
                row=0, column=0, sticky="w", pady=5)
        
        self.kullanici_adi_giris = tk.Entry(form, width=25, font=("Times New Roman", 13))
        self.kullanici_adi_giris.grid(row=0, column=1, pady=5, padx=10)
        
        
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Kaydet", width=12, 
                  font=("Times New Roman", 13),
                  command=self.save_user).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Geri", width=12, 
                  font=("Times New Roman", 13), 
                  command=self.back).grid(row=0, column=1, padx=5)
        
    def save_user(self):
        kullanici_adi = self.kullanici_adi_giris.get().strip()
        
        if not kullanici_adi:
            messagebox.showwarning("Uyarı", "Kullanıcı adı boş olamaz.", parent=self)
            return
        
        try:
            kutuphane.kullanici_ekle(kullanici_adi)
            messagebox.showinfo("Başarılı",
                                f"Kullanıcı kaydedildi!\n\n"
                                f"Ad     : {kullanici_adi}\n",
                                parent=self)
            
            #close new user page and open main window
            self.destroy()
            BookOperations(self.intro, kullanici_adi)
            
        except kullanici_mevcut:
            messagebox.showerror("Hata",
                                  f"'{kullanici_adi}' zaten kayıtlı.",
                                  parent=self)
            
    def back(self):
        self.destroy()
        self.intro.deiconify()
        


class Login(tk.Toplevel):
    
    def __init__(self, intro: Intro):
        super().__init__(intro)
        self.intro = intro 
        
        self.title("Kullanıcı Girişi")
        self.geometry("400x350")
        
        #if the user manually closes the window, the system goes back to login (intro)
        self.protocol("WM_DELETE_WINDOW", self.back)
        
        tk.Label(self, text="Kullanıcı Girişi",
                 font=("Times New Roman", 15, "bold")).pack(pady=10)
        
        form = tk.Frame(self)
        form.pack(padx=30)
        
        #--username 
        tk.Label(form, text="Kullanıcı Adı:",
                font=("Times New Roman", 13), anchor="w").grid(
                row=0, column=0, sticky="w", pady=5)
        
        self.kullanici_adi_giris = tk.Entry(form, width=25, font=("Times New Roman", 13))
        self.kullanici_adi_giris.grid(row=0, column=1, pady=5, padx=10)
        
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Giriş", width=12, 
                  font=("Times New Roman", 13),
                  command=self.check_user).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Geri", width=12, 
                  font=("Times New Roman", 13), 
                  command=self.back).grid(row=0, column=1, padx=5)
        
    def check_user(self):
        kullanici_adi = self.kullanici_adi_giris.get().strip()
        
        if not kullanici_adi:
            messagebox.showwarning("Uyarı", "Kullanıcı adı boş olamaz.", parent=self)
            return
        
        try:
            kutuphane.kullanici_bul(kullanici_adi)
            messagebox.showinfo("Başarılı",
                                f"Kullanıcının kütüphanesine girişi yapıldı!\n\n"
                                f"Ad     : {kullanici_adi}\n",
                                parent=self)
            #close login page and open main window
            self.destroy()
            BookOperations(self.intro, kullanici_adi)   
            
        except KullaniciBulunamadi:
            messagebox.showerror("Hata",
                                  f"'{kullanici_adi}' sistemde kayıtlı olarak bulunamadı.",
                                  parent=self)
            
    def back(self):
        self.destroy()
        self.intro.deiconify() 



class BookOperations(tk.Toplevel):
    
    def __init__(self, root, kullanici_adi: str):
        super().__init__(root)
        self.root = root
        self.kullanici_adi = kullanici_adi 
        
        self.title(f"LibroTrack - {kullanici_adi} Kütüphanesi")
        self.geometry("900x600")
        self.protocol("WM_DELETE_WINDOW", self.kapat)
        
        #the menu bar on the left
        self.menu_frame = tk.Frame(self, width=200, bg="#345e4e")
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.menu_frame.pack_propagate(False)   #prevents frame from shrinking depending on the contents
        
        tk.Label(self.menu_frame,
                 text=f"{kullanici_adi}",
                 bg="#5e3458", fg="white",
                 font=("Times New Roman", 18, "bold"),
                 width=15).pack(pady=15)
        
        separator_line = tk.Frame(self.menu_frame, bg="white", height=1)
        separator_line.pack(fill=tk.X, padx=10)
        
        #remainder of the page
        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.create_menu()
        self.default_screen()
        
        
    def create_menu(self):
        menu_items=[
            ("Kitaplarım", self.kitaplari_goster),
            ("Kitap Ekle", self.kitap_ekle_goster),
            ("Kitap Sil", self.kitap_sil_goster),
            ("Kitap Düzenle", self.kitap_duzenle_goster),
            ("Durum Güncelle", self.durum_guncelle_goster),
            ("Kitap Ara", self.kitap_ara_goster)]
        
        for metin, komut in menu_items:
            tk.Button(self.menu_frame, 
                      text=metin,
                      anchor=tk.W,
                      width=20,
                      bg="#345e4e",
                      fg="white",
                      activebackground="#5e3458",
                      activeforeground="white",
                      relief=tk.FLAT,
                      font=("Times New Roman", 15),
                      command=komut).pack(fill=tk.X, padx=10, pady=4)
            
    def cleanout(self):
        for widget in  self.content_frame.winfo_children():
            widget.destroy()
            
    def default_screen(self):
        self.cleanout()
        tk.Label(self.content_frame,
                 text=f"Hoş geldin {self.kullanici_adi} :)",
                 font=("Times New Roman", 20),
                 bg="white").pack(pady=40)
        tk.Label(self.content_frame,
                 text="Sol menüden istediğiniz işlemi seçiniz.",
                 font=("Times New Roman", 14),
                 bg="white").pack(pady=5)
        
    def kapat(self):
        self.destroy()
        self.root.deiconify()
        
    
    def kitaplari_goster(self):
        self.cleanout()
        
        tk.Label(self.content_frame,
                 text="Kitaplarım",
                 font=("Times New Roman", 19, "bold"),
                 bg="#5e3458",
                 fg="white").pack(pady=10)
        
        tablo_frame = tk.Frame(self.content_frame, bg="white")
        tablo_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        book_info=("id", "baslik", "yazar", "isbn", "tur", 
                   "sayfa_sayisi", "durum", "bitis_tarihi")
        
        self.tablo = ttk.Treeview(tablo_frame,
                                  columns=book_info,
                                  show="headings",
                                  selectmode="browse")
        
        self.tablo.heading("id", text="ID")
        self.tablo.heading("baslik", text="Başlık")
        self.tablo.heading("yazar", text="Yazar")
        self.tablo.heading("isbn", text="ISBN")
        self.tablo.heading("tur", text="Tür")
        self.tablo.heading("sayfa_sayisi", text="Sayfa")
        self.tablo.heading("durum", text="Durum")
        self.tablo.heading("bitis_tarihi", text="Bitiş Tarihi")
        
        self.tablo.column("id", width=45, anchor=tk.CENTER, stretch=False)
        self.tablo.column("baslik", width=150, anchor=tk.W)
        self.tablo.column("yazar", width=130, anchor=tk.W)
        self.tablo.column("isbn", width=120, anchor=tk.CENTER)
        self.tablo.column("tur", width=100, anchor=tk.W)
        self.tablo.column("sayfa_sayisi", width=70, anchor=tk.CENTER, stretch=False)
        self.tablo.column("durum", width=90, anchor=tk.CENTER)
        self.tablo.column("bitis_tarihi", width=100, anchor=tk.CENTER)
        
        dikey_scroll = ttk.Scrollbar(tablo_frame,
                                    orient=tk.VERTICAL,
                                    command=self.tablo.yview)
        yatay_scroll = ttk.Scrollbar(tablo_frame,
                                    orient=tk.HORIZONTAL,
                                    command=self.tablo.xview)
        self.tablo.configure(yscrollcommand=dikey_scroll.set,
                             xscrollcommand=yatay_scroll.set)
        
        self.tablo.grid(row=0, column=0, sticky="nsew")
        dikey_scroll.grid(row=0, column=1, sticky="ns")
        yatay_scroll.grid(row=1, column=0, sticky="ew")
        tablo_frame.rowconfigure(0, weight=1)
        tablo_frame.columnconfigure(0, weight=1)
        
        try:
            kitaplar = kutuphane.kitaplari_listele(kullanici_adi=self.kullanici_adi)
            
            if not kitaplar:
                tk.Label(self.content_frame,
                         text="Bu kullanıcıya ait kitap bulunamadı",
                         font=("Times New Roman", 15),
                         ).pack(pady=10)
                return
            
            #her kitap bir Treeview satırı
            for kitap in kitaplar:
                self.tablo.insert("",
                                  tk.END,
                                  values=kitap)
                
        except LibroTrackHatasi as error:
            messagebox.showerror("Hata oluştu.",
                                 str(error),
                                 parent=self)
            
        
    def kitap_ekle_goster(self):
        self.cleanout()
        
        tk.Label(self.content_frame,
                 text="Kitap Ekle",
                 font=("Times New Roman", 19, "bold"),
                 bg="#5e3458",
                 fg="white").pack(pady=10)
        
        form = tk.Frame(self.content_frame, bg="white")
        form.pack(pady=20)
        
        alanlar = [("Başlık", "baslik"),
                   ("Yazar", "yazar"),
                   ("ISBN", "isbn"),
                   ("Tür", "tur"),
                   ("Sayfa Sayısı", "sayfa_sayisi"),
                   ]
        
        self.girisler = {}
        
        for i, (etiket, anahtar) in enumerate(alanlar):
            tk.Label(form, text=etiket,
                     font=("Times New Roman", 15),
                     bg="white", width=15, 
                     anchor="e").grid(row=i, column=0, pady=10, padx=5)
            giris = tk.Entry(form, width=30, font=("Times New Roman", 15))
            giris.grid(row=i, column=1, pady=10, padx=5)
            self.girisler[anahtar] = giris
            
        tk.Button(self.content_frame,
                  text="Kaydet",
                  width=15,
                  font=("Times New Roman", 15),
                  command=self._kitap_kaydet).pack(pady=10)
        
        
    def _kitap_kaydet(self):
        try:
            sayfa = int(self.girisler["sayfa_sayisi"].get())
        except ValueError:
            messagebox.showerror("Hata oluştu", "Sayfa sayısı pozitif tam sayı olmalıdır.", parent=self)
            return
        
        try:
            kutuphane.kitap_ekle(kullanici_adi=self.kullanici_adi,
                                 baslik=self.girisler["baslik"].get().strip(),
                                 yazar=self.girisler["yazar"].get().strip(),
                                 isbn=self.girisler["isbn"].get().strip(),
                                 tur=self.girisler["tur"].get().strip(),
                                 sayfa_sayisi=sayfa)
            messagebox.showinfo("Başarılı", "Kitap eklendi.", parent=self)
            # refresh book list after adding
            self.kitaplari_goster()
        
        except LibroTrackHatasi as error:
            messagebox.showerror("Hata", str(error), parent=self)
        

    def kitap_sil_goster(self):
        self.cleanout()
        
        tk.Label(self.content_frame,
                 text="Kitap Sil",
                 font=("Times New Roman", 19, "bold"),
                 bg="#5e3458",
                 fg="white").pack(pady=10)
        tk.Label(self.content_frame,
                 text="Silmek istediğiniz kitabın ISBN numarasını giriniz.",
                 font=("Times New Roman", 15),
                 bg="white").pack(pady=10)
        
        form = tk.Frame(self.content_frame, bg="white")
        form.pack(pady=10)
        
        tk.Label(form, 
                 text="ISBN: ",
                 font=("Times New Roman", 15),
                 bg="white").grid(row=0, column=0, padx=5)
        self.sil_isbn = tk.Entry(form, width=25, font=("Times New Roman", 15))
        self.sil_isbn.grid(row=0, column=1, padx=5)
        
        tk.Button(self.content_frame,
                  text="Sil",
                  width=15,
                  font=("Times New Roman", 16),
                  bg="#b0073f",
                  fg="white",
                  activebackground="#b8335f",
                  command=self._kitap_sil).pack(pady=15)
        
    def _kitap_sil(self):
        isbn = self.sil_isbn.get().strip()
        if not isbn:
            messagebox.showwarning("Uyarı", "ISBN boş olamaz", parent=self)
            return
        
        onay = messagebox.askyesno("Onay",
                                   f"'{isbn}' ISBN'li kitap silinecek. Emin misiniz?",
                                   parent=self)
        if not onay:
            return
        
        try:
            kutuphane.kitap_sil(kullanici_adi=self.kullanici_adi, isbn=isbn)
            messagebox.showinfo("Başarılı", "Kitap silindi.", parent=self)
            
        except LibroTrackHatasi as error:
            messagebox.showerror("Hata", str(error), parent=self)
            
    


    #-------------------------------                             
    def kitap_duzenle_goster(self):
        self.cleanout()
        
        tk.Label(self.content_frame,
             text="Kitap Düzenle",
             font=("Times New Roman", 19, "bold"),
             bg="#5e3458", fg="white").pack(fill=tk.X, pady=10)
    
        tk.Label(self.content_frame,
                 text="Düzenlemek istediğiniz kitabın ISBN'sini girin:",
                 font=("Times New Roman", 13),
                 bg="white").pack(pady=10)
        
        isbn_frame = tk.Frame(self.content_frame, bg="white")
        isbn_frame.pack()
        
        tk.Label(isbn_frame, text="ISBN:",
                 font=("Times New Roman", 13),
                 bg="white").grid(row=0, column=0, padx=5)
        self.duzenle_isbn = tk.Entry(isbn_frame, width=25, font=("Times New Roman", 13))
        self.duzenle_isbn.grid(row=0, column=1, padx=5)
        
        tk.Button(isbn_frame, text="Kitabı Getir",
                  font=("Times New Roman", 12),
                  command=self._kitap_getir_duzenle).grid(row=0, column=2, padx=10)
        
        # form fields appear below after book is fetched
        self.duzenle_form_frame = tk.Frame(self.content_frame, bg="white")
        self.duzenle_form_frame.pack(pady=10)
    
    
    def _kitap_getir_duzenle(self):
        """ISBN ile kitabı bulur ve alanları doldurur."""
        isbn = self.duzenle_isbn.get().strip()
        if not isbn:
            messagebox.showwarning("Uyarı", "ISBN boş olamaz.", parent=self)
            return
        
        try:
            kitap = kutuphane.db.kitap_bul(
                kutuphane.db.kullanici_bul(self.kullanici_adi), isbn)
            # kitap = (id, kullanici_id, baslik, yazar, isbn, tur, sayfa_sayisi, durum, bitis_tarihi)
        except LibroTrackHatasi as error:
            messagebox.showerror("Hata", str(error), parent=self)
            return
        
        # clear previous form if any
        for widget in self.duzenle_form_frame.winfo_children():
            widget.destroy()
        
        alanlar = [
            ("Başlık",       "baslik",       kitap[2]),
            ("Yazar",        "yazar",        kitap[3]),
            ("Tür",          "tur",          kitap[5]),
            ("Sayfa Sayısı", "sayfa_sayisi", kitap[6]),
        ]
        
        self.duzenle_girisler = {}
        for i, (etiket, anahtar, mevcut_deger) in enumerate(alanlar):
            tk.Label(self.duzenle_form_frame,
                     text=etiket,
                     font=("Times New Roman", 13),
                     bg="white", width=15,
                     anchor="e").grid(row=i, column=0, pady=5, padx=5)
            giris = tk.Entry(self.duzenle_form_frame, width=30,
                             font=("Times New Roman", 13))
            giris.insert(0, str(mevcut_deger))  # pre-fill with current value
            giris.grid(row=i, column=1, pady=5, padx=5)
            self.duzenle_girisler[anahtar] = giris
        
        tk.Button(self.duzenle_form_frame,
                  text="Güncelle",
                  width=15,
                  font=("Times New Roman", 13),
                  command=lambda: self._kitap_guncelle(isbn)).grid(
                      row=len(alanlar), column=0, columnspan=2, pady=15)
    
    
    def _kitap_guncelle(self, isbn: str):
        try:
            sayfa_str = self.duzenle_girisler["sayfa_sayisi"].get()
            sayfa = int(sayfa_str) if sayfa_str else None
        except ValueError:
            messagebox.showerror("Hata", "Sayfa sayısı tam sayı olmalıdır.", parent=self)
            return
        
        try:
            kutuphane.kitap_guncelle(
                kullanici_adi=self.kullanici_adi,
                isbn=isbn,
                baslik=self.duzenle_girisler["baslik"].get().strip() or None,
                yazar=self.duzenle_girisler["yazar"].get().strip() or None,
                tur=self.duzenle_girisler["tur"].get().strip() or None,
                sayfa_sayisi=sayfa
            )
            messagebox.showinfo("Başarılı", "Kitap güncellendi.", parent=self)
            self.kitaplari_goster()
            
        except LibroTrackHatasi as error:
            messagebox.showerror("Hata", str(error), parent=self)
     
        
     
    def durum_guncelle_goster(self):
        self.cleanout()
        
        tk.Label(self.content_frame,
                 text="Okuma Durumu Güncelle",
                 font=("Times New Roman", 19, "bold"),
                 bg="#5e3458", fg="white").pack(fill=tk.X, pady=10)
        
        form = tk.Frame(self.content_frame, bg="white")
        form.pack(pady=20)
        
        tk.Label(form, text="ISBN:",
                 font=("Times New Roman", 13),
                 bg="white").grid(row=0, column=0, padx=5, pady=8)
        self.durum_isbn = tk.Entry(form, width=25, font=("Times New Roman", 13))
        self.durum_isbn.grid(row=0, column=1, padx=5, pady=8)
        
        tk.Label(form, text="Yeni Durum:",
                 font=("Times New Roman", 13),
                 bg="white").grid(row=1, column=0, padx=5, pady=8)
        
        self.durum_secim = tk.StringVar(value="okunacak")
        durum_secenekleri = ttk.Combobox(form,
                                          textvariable=self.durum_secim,
                                          values=["okunacak", "okunuyor", "okundu"],
                                          state="readonly",
                                          width=23,
                                          font=("Times New Roman", 13))
        durum_secenekleri.grid(row=1, column=1, padx=5, pady=8)
        
        tk.Button(self.content_frame,
                  text="Güncelle",
                  width=15,
                  font=("Times New Roman", 13),
                  command=self._durum_guncelle).pack(pady=15)
    
    
    def _durum_guncelle(self):
        isbn = self.durum_isbn.get().strip()
        yeni_durum = self.durum_secim.get()
        
        if not isbn:
            messagebox.showwarning("Uyarı", "ISBN boş olamaz.", parent=self)
            return
        
        try:
            kutuphane.durum_guncelle(
                kullanici_adi=self.kullanici_adi,
                isbn=isbn,
                yeni_durum=yeni_durum)
            messagebox.showinfo("Başarılı", f"Durum '{yeni_durum}' olarak güncellendi.", parent=self)
            self.kitaplari_goster()
            
        except LibroTrackHatasi as error:
            messagebox.showerror("Hata", str(error), parent=self)
          
            
    def kitap_ara_goster(self):
        self.cleanout()
        
        tk.Label(self.content_frame,
                 text="Kitap Ara",
                 font=("Times New Roman", 19, "bold"),
                 bg="#5e3458", fg="white").pack(fill=tk.X, pady=10)
        
        arama_frame = tk.Frame(self.content_frame, bg="white")
        arama_frame.pack(pady=15)
        
        tk.Label(arama_frame, text="Anahtar Kelime:",
                 font=("Times New Roman", 13),
                 bg="white").grid(row=0, column=0, padx=5)
        self.arama_giris = tk.Entry(arama_frame, width=25, font=("Times New Roman", 13))
        self.arama_giris.grid(row=0, column=1, padx=5)
        tk.Button(arama_frame, text="Ara",
                  font=("Times New Roman", 13),
                  command=self._kitap_ara).grid(row=0, column=2, padx=10)
        
        # results table
        tablo_frame = tk.Frame(self.content_frame, bg="white")
        tablo_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        kolonlar = ("baslik", "yazar", "isbn", "tur", "sayfa_sayisi", "durum")
        self.arama_tablo = ttk.Treeview(tablo_frame,
                                         columns=kolonlar,
                                         show="headings",
                                         height=12)
        for k, g in zip(kolonlar, ["Başlık", "Yazar", "ISBN", "Tür", "Sayfa", "Durum"]):
            self.arama_tablo.heading(k, text=g)
            self.arama_tablo.column(k, width=110)
        
        self.arama_tablo.pack(fill=tk.BOTH, expand=True)
    
    
    def _kitap_ara(self):
        anahtar = self.arama_giris.get().strip()
        if not anahtar:
            messagebox.showwarning("Uyarı", "Anahtar kelime boş olamaz.", parent=self)
            return
        
        # clear previous results
        for satir in self.arama_tablo.get_children():
            self.arama_tablo.delete(satir)
        
        try:
            sonuclar = kutuphane.kitap_ara(
                kullanici_adi=self.kullanici_adi,
                anahtar_kelime=anahtar)
            
            if not sonuclar:
                messagebox.showinfo("Sonuç", "Kitap bulunamadı.", parent=self)
                return
            
            for kitap in sonuclar:
                # kitap = (id, baslik, yazar, isbn, tur, sayfa_sayisi, durum, bitis_tarihi)
                self.arama_tablo.insert("", tk.END,
                                         values=(kitap[1], kitap[2], kitap[3],
                                                 kitap[4], kitap[5], kitap[6]))
        except LibroTrackHatasi as error:
            messagebox.showerror("Hata", str(error), parent=self)
                



if __name__ == "__main__":
    app = Intro()
    app.mainloop()


        
