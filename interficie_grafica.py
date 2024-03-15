from scrapper import ScrapperSBid
import tkinter as tk
from tkinter import messagebox
import json
import os

def submit_form():
    username = username_entry.get()
    password = password_entry.get()
    cycle_code = cycle_code_entry.get()
    search_option = search_option_var.get()
    search_text = search_entry.get()
    hide_browser = hide_browser_var.get()


    if username and password and cycle_code and search_option and search_text:
        root.destroy()

        
        data = {
            "username": username,
            "cycle_code": cycle_code,
            "search_option": search_option,
            "search_text": search_text,
            "hide_browser": hide_browser

        }
        with open("form_data.json", "w") as json_file:
            json.dump(data, json_file)

        messagebox.showinfo("Enviat", "Creant fitxer de dades... Si ha decidit no ocultar el navegador, siusplau, no toqui res")

        if(search_option == "codi postal"):
            scrapper = ScrapperSBid(password, search_text, cercaPerCodiPostal = True)
        else:
            scrapper = ScrapperSBid(password, search_text)

        scrapper.csv_writer()

        root.destroy()

    else:
        messagebox.showerror("Error", "Si us plau, ompliu tots els camps abans d'enviar el formulari.")

def load_saved_data():
    if os.path.exists("form_data.json"):
        with open("form_data.json", "r") as json_file:
            data = json.load(json_file)
            username_entry.insert(0, data.get("username", ""))
            cycle_code_entry.insert(0, data.get("cycle_code", ""))
            search_option_var.set(data.get("search_option", ""))
            search_entry.insert(0, data.get("search_text", ""))
            hide_browser_var.set(data.get("hide_browser", False))


def create_gui():

    messagebox.showwarning("Alerta", 
    "Utilitza aquest programa amb responsabilitat. Un us excesiu podria causar problemes en el servidor on s'allotja sBID")

    global root, username_entry, password_entry, cycle_code_entry, search_option_var, search_entry, hide_browser_var

    root = tk.Tk()
    root.title("Formulari d'entrada")

    username_label = tk.Label(root, text="Usuari:")
    username_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    username_entry = tk.Entry(root)
    username_entry.grid(row=0, column=1, padx=5, pady=5)

    password_label = tk.Label(root, text="Contrasenya:")
    password_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    password_entry = tk.Entry(root, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    cycle_code_label = tk.Label(root, text="Codi del cicle:")
    cycle_code_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
    cycle_code_entry = tk.Entry(root)
    cycle_code_entry.grid(row=2, column=1, padx=5, pady=5)

    search_option_var = tk.StringVar(value="codi postal")
    search_option_label = tk.Label(root, text="Buscar per:")
    search_option_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
    search_option_menu = tk.OptionMenu(root, search_option_var, "nom ciutat", "codi postal")
    search_option_menu.grid(row=3, column=1, padx=5, pady=5)

    search_label = tk.Label(root, text="Ciutat / Codi postal:")
    search_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
    search_entry = tk.Entry(root)
    search_entry.grid(row=4, column=1, padx=5, pady=5)

    hide_browser_var = tk.BooleanVar(value=False)
    hide_browser_checkbutton = tk.Checkbutton(root, text="Oculta navegador", variable=hide_browser_var)
    hide_browser_checkbutton.grid(row=5, columnspan=2, padx=5, pady=5)

    load_saved_data()

    submit_button = tk.Button(root, text="Enviar", command=submit_form)
    submit_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

    root.mainloop()
