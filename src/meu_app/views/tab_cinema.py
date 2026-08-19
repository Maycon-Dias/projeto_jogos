import math
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox, simpledialog
from meu_app.core.storage   import FileStorage

# ==============================================================================
# Aba 2: Reserva de Assentos para Cinema
# ==============================================================================

class CinemaTab(ttk.Frame):
    def __init__(self, parent, storage: FileStorage, rows=8, cols=10):
        super().__init__(parent)
        self.storage = storage
        self.rows = rows
        self.cols = cols
        self.seats_file = "cinema_seats.json"
        self.ranking_file = "ranking_cinema.json"
        self.seats = []
        self.buttons = {}
        self.selected_pos = None

        self.setup_ui()
        self.load_seats()

    def make_empty_seats(self):
        return [["free" for _ in range(self.cols)] for _ in range(self.rows)]

    def load_seats(self):
        data = self.storage.read_json(self.seats_file, self.make_empty_seats())
        if len(data) != self.rows or len(data[0]) != self.cols:
            self.seats = self.make_empty_seats()
            self.storage.write_json(self.seats_file, self.seats)
        else:
            self.seats = data
        self.update_grid()

    def save_seats(self):
        self.storage.write_json(self.seats_file, self.seats)

    def price_for_seat(self, row, col):
        front_rows = math.ceil(self.rows * 0.3)
        if row < front_rows:
            return 25.0
        if row < front_rows + math.ceil(self.rows * 0.4):
            return 18.0
        return 12.0

    def setup_ui(self):
        # Cabeçalho da Tela
        lbl_screen = tk.Label(self, text="--- TELA DO CINEMA ---", bg="#333", fg="white", font=("Arial", 11, "bold"), pady=4)
        lbl_screen.pack(fill="x", padx=20, pady=10)

        # Grid de Assentos
        self.grid_frame = ttk.Frame(self)
        self.grid_frame.pack(padx=20, pady=10)

        for r in range(self.rows):
            row_label = chr(65 + r)
            ttk.Label(self.grid_frame, text=row_label, font=("Arial", 9, "bold"), width=3).grid(row=r+1, column=0, padx=2, pady=2)
            for c in range(self.cols):
                if r == 0:
                    ttk.Label(self.grid_frame, text=str(c + 1), font=("Arial", 9, "bold")).grid(row=0, column=c+1, padx=2, pady=2)
                
                btn = tk.Button(self.grid_frame, text="", width=4, relief="raised",
                                command=lambda row=r, col=c: self.select_seat(row, col))
                btn.grid(row=r+1, column=c+1, padx=2, pady=2)
                self.buttons[(r, c)] = btn

        # Legenda e Detalhes
        info_frame = ttk.Frame(self)
        info_frame.pack(fill="x", padx=20, pady=5)

        ttk.Label(info_frame, text="Legenda: ").pack(side="left")
        lbl_f = tk.Label(info_frame, text="Livre", bg="#90EE90", width=8)
        lbl_f.pack(side="left", padx=2)
        lbl_r = tk.Label(info_frame, text="Reservado", bg="#FF6347", fg="white", width=10)
        lbl_r.pack(side="left", padx=2)
        lbl_b = tk.Label(info_frame, text="Bloqueado", bg="#A9A9A9", width=10)
        lbl_b.pack(side="left", padx=2)

        self.lbl_selected = ttk.Label(self, text="Nenhum assento selecionado.", font=("Arial", 10, "bold"))
        self.lbl_selected.pack(pady=5)

        # Botões de Ações
        actions_frame = ttk.Frame(self)
        actions_frame.pack(pady=5)

        self.btn_res = ttk.Button(actions_frame, text="Reservar", command=self.action_reserve)
        self.btn_res.pack(side="left", padx=5)

        self.btn_block = ttk.Button(actions_frame, text="Bloquear / Desbloquear", command=self.action_toggle_block)
        self.btn_block.pack(side="left", padx=5)

        self.btn_cancel = ttk.Button(actions_frame, text="Cancelar Reserva", command=self.action_cancel_res)
        self.btn_cancel.pack(side="left", padx=5)

        self.btn_ticket = ttk.Button(actions_frame, text="Imprimir Ingresso", command=self.action_print_ticket)
        self.btn_ticket.pack(side="left", padx=5)

    def select_seat(self, row, col):
        self.selected_pos = (row, col)
        seat_name = f"{chr(65 + row)}{col + 1}"
        status = self.seats[row][col]
        price = self.price_for_seat(row, col)
        status_map = {"free": "Livre", "reserved": "Reservado", "blocked": "Bloqueado"}
        self.lbl_selected.config(
            text=f"Assento Selecionado: {seat_name} | Estado: {status_map[status]} | Preço: R$ {price:.2f}"
        )

    def update_grid(self):
        colors = {"free": "#90EE90", "reserved": "#FF6347", "blocked": "#A9A9A9"}
        for (r, c), btn in self.buttons.items():
            status = self.seats[r][c]
            btn.config(bg=colors.get(status, "#ffffff"), text=f"{chr(65+r)}{c+1}")

    def action_reserve(self):
        if not self.selected_pos:
            messagebox.showwarning("Aviso", "Selecione um assento primeiro.")
            return
        r, c = self.selected_pos
        pos_label = f"{chr(65 + r)}{c + 1}"
        if self.seats[r][c] != "free":
            messagebox.showerror("Erro", "O assento não está livre para reserva.")
            return

        price = self.price_for_seat(r, c)
        name = simpledialog.askstring("Comprador", f"Assento {pos_label} - R$ {price:.2f}\nNome do Comprador:")
        if not name:
            return

        if messagebox.askyesno("Confirmar", f"Confirmar compra do assento {pos_label} por R$ {price:.2f}?"):
            self.seats[r][c] = "reserved"
            self.save_seats()
            self.update_grid()

            ranking = self.storage.read_json(self.ranking_file, [])
            ranking.append({
                "name": name.strip() or "Comprador",
                "score": round(price, 2),
                "date": datetime.now().isoformat(),
                "extra": {"seat": pos_label}
            })
            ranking.sort(key=lambda x: x["score"], reverse=True)
            self.storage.write_json(self.ranking_file, ranking[:100])

            self.select_seat(r, c)
            messagebox.showinfo("Sucesso", f"Compra realizada!\n\n--- INGRESSO ---\nNome: {name}\nAssento: {pos_label}\nValor: R$ {price:.2f}\nData: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    def action_toggle_block(self):
        if not self.selected_pos:
            messagebox.showwarning("Aviso", "Selecione um assento primeiro.")
            return
        r, c = self.selected_pos
        if self.seats[r][c] == "free":
            self.seats[r][c] = "blocked"
        elif self.seats[r][c] == "blocked":
            self.seats[r][c] = "free"
        else:
            messagebox.showerror("Erro", "Não é possível alterar o bloqueio de um assento já reservado.")
            return
        self.save_seats()
        self.update_grid()
        self.select_seat(r, c)

    def action_cancel_res(self):
        if not self.selected_pos:
            messagebox.showwarning("Aviso", "Selecione um assento primeiro.")
            return
        r, c = self.selected_pos
        if self.seats[r][c] != "reserved":
            messagebox.showerror("Erro", "O assento selecionado não possui reserva.")
            return
        if messagebox.askyesno("Cancelar", "Tem certeza que deseja cancelar a reserva deste assento?"):
            self.seats[r][c] = "free"
            self.save_seats()
            self.update_grid()
            self.select_seat(r, c)
            messagebox.showinfo("Cancelado", "Reserva cancelada com sucesso.")

    def action_print_ticket(self):
        if not self.selected_pos:
            messagebox.showwarning("Aviso", "Selecione um assento primeiro.")
            return
        r, c = self.selected_pos
        pos_label = f"{chr(65 + r)}{c + 1}"
        if self.seats[r][c] != "reserved":
            messagebox.showerror("Erro", "Assento não reservado. Impossível emitir ingresso.")
            return
        price = self.price_for_seat(r, c)
        messagebox.showinfo("Ingresso", f"--- INGRESSO ---\nAssento: {pos_label}\nValor: R$ {price:.2f}\nData: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n-----------------")
