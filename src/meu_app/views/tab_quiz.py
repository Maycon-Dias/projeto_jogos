import random
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from meu_app.core.storage import FileStorage

# ==============================================================================
# Aba 1: Quiz Educacional Interativo
# ==============================================================================


class QuizTab(ttk.Frame):
    def __init__(self, parent, storage: FileStorage):
        super().__init__(parent)
        self.storage = storage
        self.questions_file = "quiz_questions.json"
        self.ranking_file = "ranking_quiz.json"
        self.default_questions = [
            {
                "id": "q1",
                "question": "O que significa 'CPU' no contexto de computação?",
                "options": ["Central Processing Unit", "Computer Personal Unit", "Control Processing Unit", "Central Program Unit"],
                "answerIndex": 0,
                "phase": 1,
                "points": 10,
                "theme": "Tecnologia"
            },
            {
                "id": "q2",
                "question": "Qual a capital do Brasil?",
                "options": ["São Paulo", "Brasília", "Rio de Janeiro", "Salvador"],
                "answerIndex": 1,
                "phase": 1,
                "points": 10,
                "theme": "Cultura geral"
            },
            {
                "id": "q3",
                "question": "Qual equipamento é obrigatório para trabalhos em altura na indústria?",
                "options": ["Capacete", "Botas", "Cinto de Segurança", "Luvas"],
                "answerIndex": 2,
                "phase": 2,
                "points": 20,
                "theme": "Segurança do trabalho"
            },
            {
                "id": "q4",
                "question": "O que significa SENAI?",
                "options": ["Serviço Nacional de Aprendizagem Industrial", "Sistema Nacional de Aprendizagem Industrial", "Serviço Nacional de Apoio Industrial", "Sistema Especial Nacional de Indústria"],
                "answerIndex": 0,
                "phase": 1,
                "points": 10,
                "theme": "SENAI"
            }
        ]
        self.ensure_questions()

        self.current_player = ""
        self.total_score = 0
        self.phases = []
        self.current_phase_idx = 0
        self.current_questions = []
        self.current_question_idx = 0

        self.setup_ui()

    def ensure_questions(self):
        self.storage.read_json(self.questions_file, self.default_questions)

    def setup_ui(self):
        # Frame de Entrada do Jogador
        self.start_frame = ttk.LabelFrame(self, text="Iniciar Jogo", padding=15)
        self.start_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(self.start_frame, text="Nome do Jogador:").pack(side="left", padx=5)
        self.entry_name = ttk.Entry(self.start_frame, width=20)
        self.entry_name.pack(side="left", padx=5)
        self.entry_name.insert(0, "Jogador")

        self.btn_start = ttk.Button(self.start_frame, text="Iniciar Quiz", command=self.start_quiz)
        self.btn_start.pack(side="left", padx=10)

        # Frame da Pergunta
        self.quiz_frame = ttk.LabelFrame(self, text="Pergunta", padding=15)
        self.quiz_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.lbl_info = ttk.Label(self.quiz_frame, text="Pressione 'Iniciar Quiz' para começar.", font=("Arial", 10, "italic"))
        self.lbl_info.pack(anchor="w", pady=5)

        self.lbl_question = ttk.Label(self.quiz_frame, text="", font=("Arial", 12, "bold"), wraplength=550)
        self.lbl_question.pack(anchor="w", pady=10)

        self.opt_var = tk.IntVar(value=-1)
        self.radio_buttons = []
        for i in range(4):
            rb = ttk.Radiobutton(self.quiz_frame, text="", variable=self.opt_var, value=i)
            self.radio_buttons.append(rb)
            rb.pack(anchor="w", pady=3)

        # Botões de Ação
        self.btn_frame = ttk.Frame(self.quiz_frame)
        self.btn_frame.pack(fill="x", pady=15)

        self.btn_submit = ttk.Button(self.btn_frame, text="Confirmar Resposta", command=self.submit_answer, state="disabled")
        self.btn_submit.pack(side="left", padx=5)

        self.btn_skip = ttk.Button(self.btn_frame, text="Pular Pergunta", command=self.skip_question, state="disabled")
        self.btn_skip.pack(side="left", padx=5)

    def start_quiz(self):
        self.current_player = self.entry_name.get().strip() or "Jogador"
        all_questions = self.storage.read_json(self.questions_file, self.default_questions)
        
        phases_set = sorted(list(set(q.get("phase", 1) for q in all_questions)))
        self.phases = phases_set
        self.current_phase_idx = 0
        self.total_score = 0

        self.load_phase(all_questions)

    def load_phase(self, all_questions):
        current_phase = self.phases[self.current_phase_idx]
        phase_qs = [q for q in all_questions if q.get("phase", 1) == current_phase]
        random.shuffle(phase_qs)
        self.current_questions = phase_qs
        self.current_question_idx = 0

        self.btn_submit.config(state="normal")
        self.btn_skip.config(state="normal")
        self.display_question()

    def display_question(self):
        if self.current_question_idx < len(self.current_questions):
            q = self.current_questions[self.current_question_idx]
            curr_phase = self.phases[self.current_phase_idx]
            self.lbl_info.config(
                text=f"Fase {curr_phase} | Questão {self.current_question_idx + 1}/{len(self.current_questions)} | Pontos: {self.total_score} | Tema: {q.get('theme', 'Geral')}"
            )
            self.lbl_question.config(text=q["question"])
            self.opt_var.set(-1)

            for i, opt in enumerate(q["options"]):
                if i < len(self.radio_buttons):
                    self.radio_buttons[i].config(text=f"{i + 1}) {opt}", state="normal")
            
            # Ocultar opções extras caso tenha menos que 4
            for j in range(len(q["options"]), 4):
                self.radio_buttons[j].config(text="", state="disabled")
        else:
            self.end_phase()

    def submit_answer(self):
        choice = self.opt_var.get()
        if choice == -1:
            messagebox.showwarning("Aviso", "Selecione uma opção antes de confirmar!")
            return

        q = self.current_questions[self.current_question_idx]
        if choice == q["answerIndex"]:
            pts = q.get("points", 10)
            self.total_score += pts
            messagebox.showinfo("Correto!", f"Resposta correta! +{pts} pontos.")
        else:
            correct_text = q["options"][q["answerIndex"]]
            messagebox.showerror("Incorreto", f"Resposta errada!\nCorreta: {correct_text}")

        self.current_question_idx += 1
        self.display_question()

    def skip_question(self):
        self.current_question_idx += 1
        self.display_question()

    def end_phase(self):
        curr_phase = self.phases[self.current_phase_idx]
        msg = f"Fim da fase {curr_phase}!\nPontuação atual: {self.total_score}."

        if self.current_phase_idx + 1 < len(self.phases):
            if messagebox.askyesno("Próxima Fase", f"{msg}\nDeseja continuar para a próxima fase?"):
                self.current_phase_idx += 1
                all_questions = self.storage.read_json(self.questions_file, self.default_questions)
                self.load_phase(all_questions)
                return

        self.finish_quiz()

    def finish_quiz(self):
        self.btn_submit.config(state="disabled")
        self.btn_skip.config(state="disabled")
        self.lbl_info.config(text="Quiz Finalizado!")
        self.lbl_question.config(text=f"Parabéns {self.current_player}! Sua pontuação final foi de {self.total_score} pontos.")

        ranking = self.storage.read_json(self.ranking_file, [])
        ranking.append({
            "name": self.current_player,
            "score": self.total_score,
            "date": datetime.now().isoformat()
        })
        ranking.sort(key=lambda x: x["score"], reverse=True)
        self.storage.write_json(self.ranking_file, ranking[:50])
        messagebox.showinfo("Fim de Jogo", f"Pontuação salva com sucesso!\nTotal: {self.total_score} pontos.")
