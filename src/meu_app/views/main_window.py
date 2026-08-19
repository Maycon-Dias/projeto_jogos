import tkinter as tk
from tkinter import ttk
from meu_app.core.storage import FileStorage
from meu_app.views.tab_quiz import  QuizTab
from meu_app.views.tab_cinema import CinemaTab
from meu_app.views.tab_hangman import HangmanTab 
from meu_app.views.tab_manager import ManagerTab

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Integrado - Quiz, Cinema & Forca")
        self.geometry("760x650")
        self.resizable(False, False)

        self.storage = FileStorage("./data")

        # Configuração do Notebook (Abas)
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.tab_quiz = QuizTab(notebook, self.storage)
        self.tab_cinema = CinemaTab(notebook, self.storage, rows=8, cols=10)
        self.tab_hangman = HangmanTab(notebook, self.storage)
        self.tab_manager = ManagerTab(notebook, self.storage)

        notebook.add(self.tab_quiz, text="🎓 Quiz Educacional")
        notebook.add(self.tab_cinema, text="🎬 Reserva Cinema")
        notebook.add(self.tab_hangman, text="🪓 Jogo da Forca")
        notebook.add(self.tab_manager, text="⚙️ Gerenciamento")