import tkinter as tk
from tkinter import ttk

class LoadingScreen(ttk.Frame):
    
    def __init__(self):
        pass


    def show(self):
        self.main_window = tk.Tk()
        super().__init__(self.main_window)
        self.main_window.title("Barra de progreso en Tk")
        self.progressbar = ttk.Progressbar(self)
        self.progressbar.place(x=30, y=60, width=200)
        self.place(width=300, height=200)

        self.main_window.geometry("250x150")

        self.step = 0
        self.mainloop()

    def set_max(self, max):
        self.progressbar.configure(maximum=max)
        self.update()

    def add_step(self):
        self.step += 1
        self.progressbar.step(1)
        self.update()

    def close(self):
        self.main_window.destroy()
        


