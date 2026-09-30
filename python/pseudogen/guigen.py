import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import tkinter as tk
from tkinter import messagebox, scrolledtext

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from pseudogen import random_gen
from historand import build_figure, save_figure
from sortgen import read_numbers, sort_numbers


CHART_MAP = {
    "Гистограмма": "hist",
    "Линейный график": "line",
    "Столбчатая": "bar",
    "Круговая": "pie",
}


class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("Генератор с GUI")
        self.geometry("1442x1372")
        self.resizable(False, False)

        self.numbers = []
        self.sorted_result = []
        self.filename = "random_numbers.txt"
        self.fig = None

        self._build_ui()
        self._log("Готово к работе. Задайте диапазон и нажмите «Сгенерировать».")

    def _build_ui(self):
        header = ttk.Frame(self, padding=(24, 18, 24, 6))
        header.pack(fill="x")
        ttk.Label(header,
                  text="генератор",
                  font=("Segoe UI", 11),
                  bootstyle="secondary").pack(anchor="w")
        ttk.Label(header, text="Лабораторная работа",
                  font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(2, 0))

        body = ttk.Frame(self, padding=(24, 10, 24, 18))
        body.pack(fill="both", expand=True)

        sidebar = ttk.Frame(body, width=360)
        sidebar.pack(side="left", fill="y", padx=(0, 16))
        sidebar.pack_propagate(False)

        self._section_generation(sidebar)
        self._section_charts(sidebar)
        self._section_sorting(sidebar)

        main = ttk.Frame(body)
        main.pack(side="left", fill="both", expand=True)

        plot_card = ttk.Labelframe(main, text=" Диаграмма ",
                                   padding=12, bootstyle="secondary")
        plot_card.pack(fill="both", expand=True)

        self.plot_area = ttk.Frame(plot_card)
        self.plot_area.pack(fill="both", expand=True)

        self.plot_hint = ttk.Label(self.plot_area,
                                   text="Здесь появится диаграмма.\n"
                                        "Сначала сгенерируйте числа или нажмите «Из файла».",
                                   justify="center",
                                   bootstyle="secondary")
        self.plot_hint.pack(expand=True)

        log_card = ttk.Labelframe(main, text=" Журнал ",
                                  padding=10, bootstyle="secondary")
        log_card.pack(fill="x", pady=(16, 0))

        self.log = scrolledtext.ScrolledText(
            log_card, height=6, wrap="word",
            font=("monospace", 9), relief="flat", borderwidth=0,
            background=self.style.colors.bg, foreground=self.style.colors.fg,
        )
        self.log.pack(fill="both", expand=True)

    def _section_generation(self, parent):
        box = ttk.Labelframe(parent, text=" 1. Генерация чисел ",
                             padding=16, bootstyle="primary")
        box.pack(fill="x", pady=(0, 14))

        ttk.Label(box, text="Диапазон значений").pack(anchor="w")

        rng = ttk.Frame(box)
        rng.pack(fill="x", pady=(6, 12))
        rng.columnconfigure(0, weight=1)
        rng.columnconfigure(2, weight=1)

        self.e_min = ttk.Entry(rng, justify="center")
        self.e_min.insert(0, "1")
        self.e_min.grid(row=0, column=0, sticky="ew")

        ttk.Label(rng, text="до").grid(row=0, column=1, padx=10)

        self.e_max = ttk.Entry(rng, justify="center")
        self.e_max.insert(0, "100")
        self.e_max.grid(row=0, column=2, sticky="ew")

        ttk.Label(box, text="Количество чисел").pack(anchor="w")
        self.e_count = ttk.Entry(box)
        self.e_count.insert(0, "1000")
        self.e_count.pack(fill="x", pady=(6, 14))

        ttk.Button(box, text="Сгенерировать",
                   bootstyle="primary",
                   command=self.generate).pack(fill="x")

        self.e_count.bind("<Return>", lambda _e: self.generate())

    def _section_charts(self, parent):
        box = ttk.Labelframe(parent, text=" 2. Диаграммы ",
                             padding=16, bootstyle="info")
        box.pack(fill="x", pady=(0, 14))

        ttk.Label(box, text="Тип диаграммы").pack(anchor="w")
        self.chart_type = ttk.Combobox(box, state="readonly",
                                       values=list(CHART_MAP.keys()))
        self.chart_type.current(0)
        self.chart_type.pack(fill="x", pady=(6, 12))

        row = ttk.Frame(box)
        row.pack(fill="x", pady=(0, 8))
        ttk.Button(row, text="Из файла", bootstyle="info-outline",
                   command=self.plot_from_file).pack(
            side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(row, text="Текущий список", bootstyle="info-outline",
                   command=self.plot_current).pack(
            side="left", expand=True, fill="x", padx=(4, 0))

        ttk.Button(box, text="Сохранить в PNG",
                   bootstyle="info", command=self.save_plot).pack(fill="x")

    def _section_sorting(self, parent):
        box = ttk.Labelframe(parent, text=" 3. Сортировка ",
                             padding=16, bootstyle="success")
        box.pack(fill="x")

        ttk.Label(box, text="Порядок сортировки").pack(anchor="w")
        self.sort_choice = ttk.Combobox(
            box, state="readonly",
            values=["По убыванию (1)", "По возрастанию (2)"])
        self.sort_choice.current(0)
        self.sort_choice.pack(fill="x", pady=(6, 12))

        ttk.Button(box, text="Сортировать файл",
                   bootstyle="success",
                   command=self.sort_from_file_btn).pack(fill="x", pady=(0, 8))
        ttk.Button(box, text="Показать результат",
                   bootstyle="success-outline",
                   command=self.show_sorted).pack(fill="x")

    def _log(self, text):
        self.log.insert("end", text + "\n")
        self.log.see("end")

    def _chart_code(self):
        return CHART_MAP[self.chart_type.get()]

    def _choice(self):
        return 1 if self.sort_choice.current() == 0 else 2

    def generate(self):
        try:
            a = int(self.e_min.get())
            b = int(self.e_max.get())
            n = int(self.e_count.get())
            if n <= 0:
                raise ValueError("количество должно быть > 0")
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Проверьте числа: {e}")
            return

        self.numbers = [random_gen(a, b) for _ in range(n)]
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write("\n".join(map(str, self.numbers)))

        self._log(f"✔ Сгенерировано {n} чисел в диапазоне [{a}, {b}] → {self.filename}")

    def _draw(self, numbers):
        if not numbers:
            messagebox.showwarning("Пусто", "Нет данных для построения")
            return

        try:
            fig = build_figure(numbers, self._chart_code())
        except Exception as e:
            messagebox.showerror("Ошибка графика", str(e))
            return

        for w in self.plot_area.winfo_children():
            w.destroy()

        self.fig = fig
        canvas = FigureCanvasTkAgg(fig, master=self.plot_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def plot_from_file(self):
        try:
            numbers = read_numbers(self.filename)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return
        self._log(f"✔ Прочитано {len(numbers)} чисел из {self.filename}")
        self._draw(numbers)

    def plot_current(self):
        if not self.numbers:
            messagebox.showwarning("Нет данных", "Сначала сгенерируйте числа")
            return
        self._draw(self.numbers)

    def save_plot(self):
        if self.fig is None:
            messagebox.showwarning("Нет графика", "Сначала постройте диаграмму")
            return
        save_figure(self.fig, "histogram.png")
        self._log("✔ График сохранён в histogram.png")

    def sort_from_file_btn(self):
        try:
            numbers = read_numbers(self.filename)
            self.sorted_result = sort_numbers(numbers, self._choice())
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return

        order = "по убыванию" if self._choice() == 1 else "по возрастанию"
        head = self.sorted_result[:10]
        self._log(f"✔ Отсортировано {len(self.sorted_result)} чисел {order}. "
                  f"Первые 10: {head}")

    def show_sorted(self):
        if not self.sorted_result:
            messagebox.showinfo("Пусто", "Сначала выполните сортировку")
            return

        win = ttk.Toplevel(self)
        win.title("Отсортированный список")
        win.geometry("320x540")

        ttk.Label(win, text=f"Всего чисел: {len(self.sorted_result)}",
                  bootstyle="secondary", padding=10).pack(anchor="w")

        txt = scrolledtext.ScrolledText(win, font=("monospace", 10),
                                        relief="flat", borderwidth=0,
                                        background=self.style.colors.bg,
                                        foreground=self.style.colors.fg)
        txt.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        txt.insert("end", "\n".join(map(str, self.sorted_result)))
        txt.config(state="disabled")


if __name__ == "__main__":
    App().mainloop()