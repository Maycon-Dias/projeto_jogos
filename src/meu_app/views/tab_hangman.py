import random
import tkinter as tk
from tkinter import ttk, messagebox  
from datetime import datetime
from meu_app.core.storage import FileStorage

# ==============================================================================
# Aba 3: Jogo da Forca
# ==============================================================================

class HangmanTab(ttk.Frame):
    def __init__(self, parent, storage: FileStorage):
        super().__init__(parent)
        self.storage = storage
        self.words_file = "hangman_words.txt"
        self.ranking_file = "ranking_hangman.json"
        self.ensure_words()

        self.current_player = ""
        self.secret_word = ""
        self.attempts_left = 6
        self.guessed_letters = set()
        self.revealed = []

        self.setup_ui()

    def ensure_words(self):
        default_words = ["programacao", "typescript", "senai", "seguranca", "tecnologia", "industria", "python", "interface"]
        self.storage.read_text_file(self.words_file, "\n".join(default_words))

    def get_words(self):
        raw = self.storage.read_text_file(self.words_file, "")
        return [w.strip().lower() for w in raw.splitlines() if w.strip()]

    def setup_ui(self):
        # Frame de Entrada
        self.start_frame = ttk.LabelFrame(self, text="Iniciar Novo Jogo", padding=10)
        self.start_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(self.start_frame, text="Jogador:").pack(side="left", padx=5)
        self.entry_player = ttk.Entry(self.start_frame, width=18)
        self.entry_player.pack(side="left", padx=5)
        self.entry_player.insert(0, "Jogador")

        self.btn_start = ttk.Button(self.start_frame, text="Novo Jogo", command=self.start_game)
        self.btn_start.pack(side="left", padx=10)

        # Área de Exibição
        self.game_frame = ttk.LabelFrame(self, text="Partida", padding=15)
        self.game_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.lbl_word = ttk.Label(self.game_frame, text="_ _ _ _ _", font=("Consolas", 24, "bold"))
        self.lbl_word.pack(pady=15)

        self.lbl_attempts = ttk.Label(self.game_frame, text="Tentativas restantes: 6", font=("Arial", 11))
        self.lbl_attempts.pack(pady=2)

        self.lbl_guessed = ttk.Label(self.game_frame, text="Letras chutadas: -", font=("Arial", 10, "italic"))
        self.lbl_guessed.pack(pady=2)

        # Chutes
        guess_frame = ttk.Frame(self.game_frame)
        guess_frame.pack(pady=15)

        ttk.Label(guess_frame, text="Letra ou Palavra:").pack(side="left", padx=5)
        self.entry_guess = ttk.Entry(guess_frame, width=12, state="disabled")
        self.entry_guess.pack(side="left", padx=5)
        self.entry_guess.bind("<Return>", lambda event: self.submit_guess())

        self.btn_guess = ttk.Button(guess_frame, text="Chutar", command=self.submit_guess, state="disabled")
        self.btn_guess.pack(side="left", padx=5)

    def start_game(self):
        words = self.get_words()
        if not words:
            messagebox.showerror("Erro", "Nenhuma palavra disponível.")
            return

        self.current_player = self.entry_player.get().strip() or "Jogador"
        self.secret_word = random.choice(words).lower()
        self.attempts_left = 6
        self.guessed_letters = set()
        self.revealed = [" " if ch == " " else "_" for ch in self.secret_word]

        self.btn_guess.config(state="normal")
        self.entry_guess.config(state="normal")
        self.entry_guess.delete(0, tk.END)
        self.entry_guess.focus()

        self.update_screen()

    def update_screen(self):
        self.lbl_word.config(text=" ".join(self.revealed))
        self.lbl_attempts.config(text=f"Tentativas restantes: {self.attempts_left}")
        sorted_guesses = sorted(list(self.guessed_letters))
        self.lbl_guessed.config(text=f"Letras chutadas: {', '.join(sorted_guesses) if sorted_guesses else '-'}")

    def submit_guess(self):
        guess = self.entry_guess.get().strip().lower()
        self.entry_guess.delete(0, tk.END)

        if not guess:
            return

        if len(guess) == 1:
            if guess in self.guessed_letters:
                messagebox.showwarning("Aviso", "Você já tentou esta letra.")
                return
            self.guessed_letters.add(guess)

            if guess in self.secret_word:
                for i, ch in enumerate(self.secret_word):
                    if ch == guess:
                        self.revealed[i] = guess
            else:
                self.attempts_left -= 1
        else:
            # Chute de palavra completa
            if guess == self.secret_word:
                self.revealed = list(self.secret_word)
            else:
                self.attempts_left = max(0, self.attempts_left - 2)
                messagebox.showwarning("Erro", "Palavra incorreta! Penalidade: -2 tentativas.")

        self.update_screen()
        self.check_game_over()

    def check_game_over(self):
        if "_" not in self.revealed:
            score = (self.attempts_left * 10) + (len(self.secret_word) * 2)
            ranking = self.storage.read_json(self.ranking_file, [])
            ranking.append({
                "name": self.current_player,
                "score": score,
                "date": datetime.now().isoformat(),
                "extra": {"word": self.secret_word}
            })
            ranking.sort(key=lambda x: x["score"], reverse=True)
            self.storage.write_json(self.ranking_file, ranking[:50])

            messagebox.showinfo("Vitória!", f"Parabéns {self.current_player}!\nVocê acertou a palavra: {self.secret_word}\nPontuação: {score}")
            self.end_game()

        elif self.attempts_left <= 0:
            messagebox.showerror("Derrota", f"Fim de jogo! Você perdeu.\nA palavra era: {self.secret_word}")
            self.end_game()

    def end_game(self):
        self.btn_guess.config(state="disabled")
        self.entry_guess.config(state="disabled")