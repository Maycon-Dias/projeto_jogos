import os
import math
import random
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from meu_app.core.storage import FileStorage

# ==============================================================================
# Aba 4: Gerenciamento & Rankings
# ==============================================================================

class ManagerTab(ttk.Frame):
    def __init__(self, parent, storage: FileStorage):
        super().__init__(parent)
        self.storage = storage
        self.setup_ui()

    def setup_ui(self):
        # Ações de Gerenciamento
        top_frame = ttk.LabelFrame(self, text="Gerenciamento de Registros", padding=10)
        top_frame.pack(fill="x", padx=15, pady=10)

        ttk.Button(top_frame, text="Adicionar Pergunta ao Quiz", command=self.add_quiz_question).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Adicionar Palavra à Forca", command=self.add_hangman_word).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Carregar Rankings", command=self.load_rankings).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Resetar Todos os Dados", command=self.reset_data).pack(side="left", padx=5)

        # Exibição de Rankings
        rank_frame = ttk.LabelFrame(self, text="Rankings Locais (Top 10)", padding=10)
        rank_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.txt_ranking = tk.Text(rank_frame, height=18, wrap="word", font=("Consolas", 10))
        self.txt_ranking.pack(fill="both", expand=True)

    def add_quiz_question(self):
        q = simpledialog.askstring("Nova Pergunta", "Digite o texto da pergunta:")
        if not q:
            return
        opts_raw = simpledialog.askstring("Opções", "Digite 4 opções separadas por ';' (Ex: Op1;Op2;Op3;Op4):")
        if not opts_raw:
            return
        options = [o.strip() for o in opts_raw.split(";") if o.strip()]
        if len(options) < 2:
            messagebox.showerror("Erro", "Insira pelo menos 2 opções válidas.")
            return

        idx_str = simpledialog.askstring("Índice", f"Qual o número da opção correta (1-{len(options)}):")
        try:
            ans_idx = int(idx_str) - 1
            if not (0 <= ans_idx < len(options)):
                raise ValueError()
        except Exception:
            messagebox.showerror("Erro", "Índice de resposta inválido.")
            return

        phase_str = simpledialog.askstring("Fase", "Fase/Nível (Ex: 1, 2, 3):") or "1"
        pts_str = simpledialog.askstring("Pontos", "Pontuação (Ex: 10, 20):") or "10"
        theme = simpledialog.askstring("Tema", "Tema da pergunta:") or "Geral"

        new_question = {
            "id": f"q{int(datetime.now().timestamp()*1000)}",
            "question": q,
            "options": options,
            "answerIndex": ans_idx,
            "phase": int(phase_str) if phase_str.isdigit() else 1,
            "points": int(pts_str) if pts_str.isdigit() else 10,
            "theme": theme
        }

        qs = self.storage.read_json("quiz_questions.json", [])
        qs.append(new_question)
        self.storage.write_json("quiz_questions.json", qs)
        messagebox.showinfo("Sucesso", "Pergunta adicionada ao banco do Quiz!")

    def add_hangman_word(self):
        word = simpledialog.askstring("Nova Palavra", "Digite a palavra para a Forca:")
        if word and word.strip():
            self.storage.append_text_file("hangman_words.txt", f"\n{word.strip().lower()}")
            messagebox.showinfo("Sucesso", f"Palavra '{word.strip()}' adicionada com sucesso!")

    def load_rankings(self):
        r_quiz = self.storage.read_json("ranking_quiz.json", [])
        r_cinema = self.storage.read_json("ranking_cinema.json", [])
        r_hang = self.storage.read_json("ranking_hangman.json", [])

        self.txt_ranking.delete("1.0", tk.END)

        def format_section(title, data, unit="pts"):
            out = f"=== {title} ===\n"
            if not data:
                out += "  (Nenhum registro encontrado)\n"
            for i, r in enumerate(data[:10]):
                extra = f" [{r.get('extra')}]" if r.get('extra') else ""
                val = f"R$ {r['score']:.2f}" if unit == "R$" else f"{r['score']} {unit}"
                out += f"  {i+1}. {r['name']} - {val}{extra}\n"
            out += "\n"
            return out

        content = format_section("RANKING QUIZ", r_quiz, "pontos")
        content += format_section("RANKING VENDAS CINEMA", r_cinema, "R$")
        content += format_section("RANKING FORCA", r_hang, "pontos")

        self.txt_ranking.insert(tk.END, content)

    def reset_data(self):
        if messagebox.askyesno("Resetar", "Tem certeza que deseja apagar todos os dados salvos em ./data?"):
            for f in os.listdir(self.storage.base_dir):
                file_path = os.path.join(self.storage.base_dir, f)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception:
                    pass
            self.txt_ranking.delete("1.0", tk.END)
            messagebox.showinfo("Concluído", "Todos os dados foram resetados!")