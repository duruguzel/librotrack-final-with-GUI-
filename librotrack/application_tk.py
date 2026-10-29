import tkinter as tk
from tkinter import messagebox

from src.config import load_config
from src.database import VeritabaniYoneticisi
from src.library import Kutuphane
from src.exceptions import kullanici_mevcut, KullaniciBulunamadi

config = load_config()
db = VeritabaniYoneticisi(config["database"]["path"])
kutuphane = Kutuphane(db)


def cont():
    user_choice = user_status.get()
    print(user_choice)
    if user_choice == 1:
        root.withdraw()
        open_login()
    elif user_choice == 2:
        root.withdraw()
        open_new_user()


def open_new_user():
    win = tk.Toplevel(root)
    win.title("Yeni Kullanıcı Kaydı")
    win.geometry("400x350")
    win.protocol("WM_DELETE_WINDOW", lambda: [win.destroy(), root.deiconify()])

    tk.Label(win, text="Yeni Kullanıcı Kaydı",
             font=("Times New Roman", 15, "bold")).pack(pady=10)

    form = tk.Frame(win)
    form.pack(padx=30)

    tk.Label(form, text="Kullanıcı Adı:",
             font=("Times New Roman", 13)).grid(row=0, column=0, sticky="w", pady=5)
    kullanici_entry = tk.Entry(form, width=25, font=("Times New Roman", 13))
    kullanici_entry.grid(row=0, column=1, pady=5, padx=10)

    def save_user():
        kullanici_adi = kullanici_entry.get().strip()
        if not kullanici_adi:
            messagebox.showwarning("Uyarı", "Kullanıcı adı boş olamaz.", parent=win)
            return
        try:
            kutuphane.kullanici_ekle(kullanici_adi)
            messagebox.showinfo("Başarılı", f"Kullanıcı kaydedildi: {kullanici_adi}", parent=win)
            win.destroy()
            root.deiconify()
        except kullanici_mevcut:
            messagebox.showerror("Hata", f"'{kullanici_adi}' zaten kayıtlı.", parent=win)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=20)
    tk.Button(btn_frame, text="Kaydet", width=12,
              font=("Times New Roman", 13),
              command=save_user).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Geri", width=12,
              font=("Times New Roman", 13),
              command=lambda: [win.destroy(), root.deiconify()]).pack(side=tk.LEFT, padx=5)


def open_login():
    win = tk.Toplevel(root)
    win.title("Kullanıcı Girişi")
    win.geometry("400x350")
    win.protocol("WM_DELETE_WINDOW", lambda: [win.destroy(), root.deiconify()])

    tk.Label(win, text="Kullanıcı Girişi",
             font=("Times New Roman", 15, "bold")).pack(pady=10)

    form = tk.Frame(win)
    form.pack(padx=30)

    tk.Label(form, text="Kullanıcı Adı:",
             font=("Times New Roman", 13)).grid(row=0, column=0, sticky="w", pady=5)
    kullanici_entry = tk.Entry(form, width=25, font=("Times New Roman", 13))
    kullanici_entry.grid(row=0, column=1, pady=5, padx=10)

    def check_user():
        kullanici_adi = kullanici_entry.get().strip()
        if not kullanici_adi:
            messagebox.showwarning("Uyarı", "Kullanıcı adı boş olamaz.", parent=win)
            return
        try:
            kutuphane.kullanici_bul(kullanici_adi)
            messagebox.showinfo("Başarılı", f"Giriş yapıldı: {kullanici_adi}", parent=win)
            win.destroy()
            root.deiconify()
        except KullaniciBulunamadi:
            messagebox.showerror("Hata", f"'{kullanici_adi}' bulunamadı.", parent=win)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=20)
    tk.Button(btn_frame, text="Giriş", width=12,
              font=("Times New Roman", 13),
              command=check_user).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Geri", width=12,
              font=("Times New Roman", 13),
              command=lambda: [win.destroy(), root.deiconify()]).pack(side=tk.LEFT, padx=5)


# main window
root = tk.Tk()
root.title("LibroTrack - Kullanıcı Girişi")
root.geometry("500x350")

tk.Label(root, text="LibroTrack",
         font=("Times New Roman", 20, "bold")).pack(pady=20)
tk.Label(root, text="Kullanıcı seçin veya kullanıcı ekleyin",
         font=("Times New Roman", 15)).pack(pady=5)

user_status = tk.IntVar(master=root, value=1)

tk.Radiobutton(root, text="Kayıtlı kullanıcı girişi",
               variable=user_status, value=1,
               font=("Times New Roman", 13)).pack(anchor=tk.W, padx=40)
tk.Radiobutton(root, text="Yeni kullanıcı kaydı",
               variable=user_status, value=2,
               font=("Times New Roman", 13)).pack(anchor=tk.W, padx=40)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=20)
tk.Button(btn_frame, text="Enter", width=10,
          command=cont).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Close", width=10,
          command=root.destroy).pack(side=tk.LEFT, padx=5)

root.mainloop()