"""
╔══════════════════════════════════════════════════════════╗
║          MicroC COMPILER  v1.0  — Pre-Compilador         ║
║          Universidad Mesoamericana  |  2026              ║
║          Autómatas y Lenguajes  —  Ing. Baudilio Boteo   ║
╚══════════════════════════════════════════════════════════╝
  Extras únicos:
    • Resaltado de sintaxis en tiempo real
    • Numeración de líneas
    • Contador de tokens léxicos en vivo
    • Reloj en tiempo real en la barra superior
    • Animación de "typing" al abrir archivos
    • Estadísticas del código (Ctrl+T)
    • Análisis léxico con reporte detallado
    • Auto-indentación al presionar Enter
    • Tema retro-terminal Cyberpunk
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os, re, datetime, threading, time

# ══════════════════════════════════════════════════════════
#  PALETA DE COLORES — Retro Terminal / Cyberpunk
# ══════════════════════════════════════════════════════════
BG_MAIN    = "#0a0a0f"
BG_PANEL   = "#0d0d15"
BG_HEADER  = "#080810"
NEON_GREEN = "#00ff88"
NEON_AMBER = "#ffb300"
NEON_CYAN  = "#00e5ff"
NEON_PINK  = "#ff0080"
NEON_BLUE  = "#4488ff"
DIM_GREEN  = "#00aa55"
TEXT_MAIN  = "#ccffcc"
TEXT_DIM   = "#336633"
CURSOR_CLR = "#00ff88"

KEYWORDS = [
    'int','float','char','void','return','if','else','while',
    'for','do','break','continue','printf','scanf','main',
    'include','define','struct','typedef','switch','case',
    'default','const','static','extern','sizeof'
]

# ══════════════════════════════════════════════════════════
class MicroCCompiler(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MicroC COMPILER v1.0")
        self.geometry("1280x760")
        self.configure(bg=BG_MAIN)
        self.minsize(900, 600)

        self.current_file   = None
        self.is_new_file    = True
        self.is_editable    = False
        self.is_modified    = False
        self._clock_running = True

        self._build_ui()
        self._bind_events()
        self._update_title()
        self._start_clock()
        self._boot_sequence()

    # ──────────────────────────────────────────────────────
    def _build_ui(self):
        # MENÚ
        menubar = tk.Menu(self, bg=BG_HEADER, fg=NEON_GREEN,
                          activebackground=NEON_GREEN, activeforeground=BG_MAIN,
                          relief="flat", bd=0, font=("Courier New", 10))
        self.config(menu=menubar)

        def make_menu(label, items):
            m = tk.Menu(menubar, tearoff=0, bg=BG_PANEL, fg=NEON_GREEN,
                        activebackground=NEON_GREEN, activeforeground=BG_MAIN,
                        relief="flat", bd=1, font=("Courier New", 10))
            for it in items:
                if it == "---":
                    m.add_separator()
                else:
                    m.add_command(label=it[0], command=it[1])
            menubar.add_cascade(label=label, menu=m)

        make_menu("[ ARCHIVO ]", [
            ("  >> NUEVO          Ctrl+N", self.cmd_nuevo),
            ("  >> ABRIR          Ctrl+O", self.cmd_abrir),
            ("  >> GUARDAR        Ctrl+S", self.cmd_guardar),
            "---",
            ("  >> ESTADÍSTICAS   Ctrl+T", self.cmd_stats),
            "---",
            ("  >> SALIR", self.cmd_salir),
        ])
        make_menu("[ EDITAR ]", [
            ("  >> HABILITAR EDICIÓN  Ctrl+E", self.cmd_editar),
            ("  >> DESHACER           Ctrl+Z", lambda: self.txt_editor.edit_undo()),
            ("  >> REHACER            Ctrl+Y", lambda: self.txt_editor.edit_redo()),
        ])
        make_menu("[ COMPILAR ]", [
            ("  >> COMPILAR  F5",      self.cmd_compilar),
            ("  >> LIMPIAR CONSOLA",   self._limpiar_consola),
        ])
        make_menu("[ AYUDA ]", [
            ("  >> ATAJOS / AYUDA",    self.cmd_ayuda),
            ("  >> ACERCA DE",         self.cmd_acerca),
        ])

        # HEADER
        header = tk.Frame(self, bg=BG_HEADER, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="◈ MicroC COMPILER",
                 bg=BG_HEADER, fg=NEON_GREEN,
                 font=("Courier New", 16, "bold")).pack(side="left", padx=16)
        tk.Label(header, text="PRE-COMPILADOR  |  UNIV. MESOAMERICANA  |  2026",
                 bg=BG_HEADER, fg=DIM_GREEN,
                 font=("Courier New", 9)).pack(side="left", padx=4)
        self.lbl_clock = tk.Label(header, text="",
                                   bg=BG_HEADER, fg=NEON_AMBER,
                                   font=("Courier New", 11, "bold"))
        self.lbl_clock.pack(side="right", padx=16)

        # TOOLBAR
        tk.Frame(self, bg=NEON_GREEN, height=1).pack(fill="x")
        toolbar = tk.Frame(self, bg=BG_PANEL, height=42)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        btns = [
            ("[ NUEVO ]",    self.cmd_nuevo,    NEON_GREEN),
            ("[ ABRIR ]",    self.cmd_abrir,    NEON_GREEN),
            ("[ GUARDAR ]",  self.cmd_guardar,  NEON_GREEN),
            ("[ EDITAR ]",   self.cmd_editar,   NEON_AMBER),
            ("[ COMPILAR ]", self.cmd_compilar, NEON_CYAN),
            ("[ STATS ]",    self.cmd_stats,    NEON_PINK),
            ("[ AYUDA ]",    self.cmd_ayuda,    DIM_GREEN),
            ("[ SALIR ]",    self.cmd_salir,    NEON_PINK),
        ]
        for text, cmd, color in btns:
            b = tk.Button(toolbar, text=text, command=cmd,
                          bg=BG_PANEL, fg=color, relief="flat", bd=0,
                          font=("Courier New", 9, "bold"),
                          padx=10, pady=8, cursor="hand2",
                          activebackground=color, activeforeground=BG_MAIN)
            b.pack(side="left", padx=1)
            b.bind("<Enter>", lambda e, btn=b, c=color: btn.config(bg=c, fg=BG_MAIN))
            b.bind("<Leave>", lambda e, btn=b, c=color: btn.config(bg=BG_PANEL, fg=c))

        tk.Frame(self, bg=DIM_GREEN, height=1).pack(fill="x")

        # ÁREA PRINCIPAL
        main = tk.Frame(self, bg=BG_MAIN)
        main.pack(fill="both", expand=True)

        # PANEL IZQUIERDO — editor
        left = tk.Frame(main, bg=BG_MAIN)
        left.pack(side="left", fill="both", expand=True)

        ed_hdr = tk.Frame(left, bg=BG_HEADER, height=28)
        ed_hdr.pack(fill="x")
        ed_hdr.pack_propagate(False)
        tk.Label(ed_hdr, text=" ◈ EDITOR  [ TextBox1 ]",
                 bg=BG_HEADER, fg=NEON_GREEN,
                 font=("Courier New", 9, "bold")).pack(side="left", padx=8)
        self.lbl_modo = tk.Label(ed_hdr, text="█ BLOQUEADO",
                                  bg=BG_HEADER, fg=NEON_PINK,
                                  font=("Courier New", 9, "bold"))
        self.lbl_modo.pack(side="right", padx=8)
        self.lbl_file = tk.Label(ed_hdr, text="sin-titulo.c",
                                  bg=BG_HEADER, fg=NEON_AMBER,
                                  font=("Courier New", 9))
        self.lbl_file.pack(side="right", padx=8)

        ed_cont = tk.Frame(left, bg=BG_MAIN)
        ed_cont.pack(fill="both", expand=True)

        self.line_numbers = tk.Text(ed_cont, width=5,
                                     bg=BG_HEADER, fg=DIM_GREEN,
                                     font=("Courier New", 12),
                                     state="disabled", relief="flat", bd=0,
                                     padx=4, pady=2, cursor="arrow",
                                     selectbackground=BG_HEADER)
        self.line_numbers.pack(side="left", fill="y")
        tk.Frame(ed_cont, bg=DIM_GREEN, width=1).pack(side="left", fill="y")

        self.txt_editor = tk.Text(ed_cont,
                                   bg=BG_MAIN, fg=TEXT_MAIN,
                                   insertbackground=CURSOR_CLR,
                                   font=("Courier New", 12),
                                   relief="flat", bd=0,
                                   padx=12, pady=4,
                                   selectbackground="#003322",
                                   selectforeground=NEON_GREEN,
                                   undo=True, state="disabled",
                                   wrap="none", spacing1=2, spacing3=2)
        self.txt_editor.pack(side="left", fill="both", expand=True)

        sc_y = tk.Scrollbar(ed_cont, command=self._sync_scroll,
                             bg=BG_PANEL, troughcolor=BG_MAIN,
                             relief="flat", width=10)
        sc_y.pack(side="right", fill="y")
        self.txt_editor.config(yscrollcommand=sc_y.set)

        sc_x = tk.Scrollbar(left, orient="horizontal",
                             command=self.txt_editor.xview,
                             bg=BG_PANEL, troughcolor=BG_MAIN,
                             relief="flat", width=8)
        sc_x.pack(fill="x")
        self.txt_editor.config(xscrollcommand=sc_x.set)

        # DIVISOR
        tk.Frame(main, bg=NEON_GREEN, width=1).pack(side="left", fill="y")

        # PANEL DERECHO — consola
        right = tk.Frame(main, bg=BG_MAIN, width=420)
        right.pack(side="right", fill="both")
        right.pack_propagate(False)

        con_hdr = tk.Frame(right, bg=BG_HEADER, height=28)
        con_hdr.pack(fill="x")
        con_hdr.pack_propagate(False)
        tk.Label(con_hdr, text=" ◈ CONSOLA  [ TextBox2 ]",
                 bg=BG_HEADER, fg=NEON_CYAN,
                 font=("Courier New", 9, "bold")).pack(side="left", padx=8)
        tk.Button(con_hdr, text="[ CLR ]", command=self._limpiar_consola,
                  bg=BG_HEADER, fg=DIM_GREEN, relief="flat", bd=0,
                  cursor="hand2", font=("Courier New", 9),
                  activebackground=NEON_PINK,
                  activeforeground=BG_MAIN).pack(side="right", padx=8)

        self.txt_output = tk.Text(right,
                                   bg=BG_PANEL, fg=NEON_GREEN,
                                   insertbackground=NEON_GREEN,
                                   font=("Courier New", 11),
                                   relief="flat", bd=0,
                                   padx=10, pady=6,
                                   state="disabled", wrap="word", spacing1=1)
        self.txt_output.pack(fill="both", expand=True)

        sc_con = tk.Scrollbar(right, command=self.txt_output.yview,
                               bg=BG_PANEL, troughcolor=BG_MAIN,
                               relief="flat", width=8)
        sc_con.pack(side="right", fill="y")
        self.txt_output.config(yscrollcommand=sc_con.set)

        # BARRA DE ESTADO
        tk.Frame(self, bg=NEON_GREEN, height=1).pack(fill="x")
        status = tk.Frame(self, bg=BG_HEADER, height=26)
        status.pack(fill="x", side="bottom")
        status.pack_propagate(False)

        self.lbl_status = tk.Label(status, text="  SISTEMA LISTO >_",
                                    bg=BG_HEADER, fg=NEON_GREEN,
                                    font=("Courier New", 9), anchor="w")
        self.lbl_status.pack(side="left", fill="x", expand=True, padx=4)

        self.lbl_tokens = tk.Label(status, text="TOKENS: 0",
                                    bg=BG_HEADER, fg=NEON_AMBER,
                                    font=("Courier New", 9))
        self.lbl_tokens.pack(side="right", padx=8)

        self.lbl_cursor = tk.Label(status, text="LN:1  COL:1",
                                    bg=BG_HEADER, fg=NEON_CYAN,
                                    font=("Courier New", 9))
        self.lbl_cursor.pack(side="right", padx=8)

        self.lbl_lines = tk.Label(status, text="LÍNEAS: 0",
                                   bg=BG_HEADER, fg=DIM_GREEN,
                                   font=("Courier New", 9))
        self.lbl_lines.pack(side="right", padx=8)

        self._setup_tags()

    def _setup_tags(self):
        self.txt_editor.tag_configure("keyword",  foreground=NEON_CYAN,  font=("Courier New", 12, "bold"))
        self.txt_editor.tag_configure("string",   foreground=NEON_AMBER)
        self.txt_editor.tag_configure("comment",  foreground=TEXT_DIM,   font=("Courier New", 12, "italic"))
        self.txt_editor.tag_configure("number",   foreground=NEON_PINK)
        self.txt_editor.tag_configure("include",  foreground=NEON_GREEN, font=("Courier New", 12, "bold"))
        self.txt_editor.tag_configure("operator", foreground=NEON_AMBER)
        self.txt_editor.tag_configure("brace",    foreground=NEON_GREEN, font=("Courier New", 12, "bold"))

        self.txt_output.tag_configure("ok",     foreground=NEON_GREEN)
        self.txt_output.tag_configure("error",  foreground=NEON_PINK)
        self.txt_output.tag_configure("warn",   foreground=NEON_AMBER)
        self.txt_output.tag_configure("info",   foreground=NEON_CYAN)
        self.txt_output.tag_configure("dim",    foreground=DIM_GREEN)
        self.txt_output.tag_configure("accent", foreground=NEON_GREEN, font=("Courier New", 11, "bold"))

    # ──────────────────────────────────────────────────────
    def _bind_events(self):
        self.bind("<Control-n>", lambda e: self.cmd_nuevo())
        self.bind("<Control-o>", lambda e: self.cmd_abrir())
        self.bind("<Control-s>", lambda e: self.cmd_guardar())
        self.bind("<Control-e>", lambda e: self.cmd_editar())
        self.bind("<Control-t>", lambda e: self.cmd_stats())
        self.bind("<F5>",        lambda e: self.cmd_compilar())
        self.protocol("WM_DELETE_WINDOW", self.cmd_salir)
        self.txt_editor.bind("<KeyRelease>",    self._on_key)
        self.txt_editor.bind("<ButtonRelease>", self._update_cursor)
        self.txt_editor.bind("<Return>",        self._auto_indent)

    def _on_key(self, e=None):
        self.is_modified = True
        self._update_line_numbers()
        self._highlight_syntax()
        self._update_cursor()
        self._update_token_count()
        self._update_title()

    def _auto_indent(self, e=None):
        idx  = self.txt_editor.index(tk.INSERT)
        ln   = int(idx.split(".")[0])
        line = self.txt_editor.get(f"{ln}.0", f"{ln}.end")
        spaces = len(line) - len(line.lstrip())
        if line.rstrip().endswith("{"):
            spaces += 4
        self.after(1, lambda: self.txt_editor.insert(tk.INSERT, " " * spaces))

    def _sync_scroll(self, *args):
        self.txt_editor.yview(*args)
        self.line_numbers.yview(*args)

    def _update_cursor(self, e=None):
        pos = self.txt_editor.index(tk.INSERT)
        ln, col = pos.split(".")
        self.lbl_cursor.config(text=f"LN:{ln}  COL:{int(col)+1}")

    def _update_line_numbers(self):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        n = self.txt_editor.get("1.0", tk.END).count("\n")
        self.line_numbers.insert("1.0", "\n".join(f"{i:>3}" for i in range(1, n + 1)))
        self.line_numbers.config(state="disabled")
        self.lbl_lines.config(text=f"LÍNEAS: {n}")

    def _update_token_count(self):
        content = self.txt_editor.get("1.0", tk.END)
        tokens  = re.findall(r'\b\w+\b|[+\-*/=<>!&|;,(){}]', content)
        self.lbl_tokens.config(text=f"TOKENS: {len(tokens)}")

    def _update_title(self):
        mod  = " [*]" if self.is_modified else ""
        name = os.path.basename(self.current_file) if self.current_file else "sin-titulo.c"
        self.title(f"MicroC COMPILER v1.0  —  {name}{mod}")
        self.lbl_file.config(text=name + mod)

    def _start_clock(self):
        def tick():
            while self._clock_running:
                now = datetime.datetime.now().strftime("%H:%M:%S  %d/%m/%Y")
                try:
                    self.lbl_clock.config(text=f"⬡ {now}")
                except:
                    break
                time.sleep(1)
        threading.Thread(target=tick, daemon=True).start()

    def _boot_sequence(self):
        msgs = [
            ("╔══════════════════════════════════════════╗\n", "accent"),
            ("║     MicroC COMPILER  v1.0                ║\n", "accent"),
            ("║     Pre-Compilador  —  2026              ║\n", "accent"),
            ("╚══════════════════════════════════════════╝\n", "accent"),
            ("\n", "dim"),
            ("[ OK ] Iniciando sistema...\n",        "ok"),
            ("[ OK ] Cargando módulo editor...\n",   "ok"),
            ("[ OK ] Resaltado de sintaxis listo\n", "ok"),
            ("[ OK ] Analizador léxico en espera\n", "ok"),
            ("\n", "dim"),
            ("─────────────────────────────────────────\n", "dim"),
            (" ATAJOS:  Ctrl+N  Ctrl+O  Ctrl+S  F5\n", "info"),
            ("─────────────────────────────────────────\n", "dim"),
            ("\n", "dim"),
            (" > SISTEMA LISTO. ESPERANDO CÓDIGO...\n", "accent"),
        ]
        def show(i=0):
            if i < len(msgs):
                self._log(msgs[i][0], msgs[i][1])
                self.after(60, lambda: show(i + 1))
        self.after(300, lambda: show())

    # ──────────────────────────────────────────────────────
    def _highlight_syntax(self):
        for tag in ("keyword","string","comment","number","include","operator","brace"):
            self.txt_editor.tag_remove(tag, "1.0", tk.END)
        lines = self.txt_editor.get("1.0", tk.END).split("\n")
        for i, line in enumerate(lines, 1):
            ln = f"{i}."
            if re.search(r'//.*', line):
                m = re.search(r'//.*', line)
                self.txt_editor.tag_add("comment", f"{ln}{m.start()}", f"{ln}{m.end()}")
                continue
            m = re.match(r'^\s*#\w+', line)
            if m:
                self.txt_editor.tag_add("include", f"{ln}0", f"{ln}{m.end()}")
            for m in re.finditer(r'"[^"]*"', line):
                self.txt_editor.tag_add("string", f"{ln}{m.start()}", f"{ln}{m.end()}")
            for m in re.finditer(r'\b\d+\.?\d*\b', line):
                self.txt_editor.tag_add("number", f"{ln}{m.start()}", f"{ln}{m.end()}")
            for kw in KEYWORDS:
                for m in re.finditer(rf'\b{kw}\b', line):
                    self.txt_editor.tag_add("keyword", f"{ln}{m.start()}", f"{ln}{m.end()}")
            for m in re.finditer(r'[{}()\[\]]', line):
                self.txt_editor.tag_add("brace", f"{ln}{m.start()}", f"{ln}{m.end()}")
            for m in re.finditer(r'[+\-*/%=<>!&|]', line):
                self.txt_editor.tag_add("operator", f"{ln}{m.start()}", f"{ln}{m.end()}")

    # ──────────────────────────────────────────────────────
    #  COMANDOS
    # ──────────────────────────────────────────────────────
    def cmd_nuevo(self):
        if self.is_modified and not self._ask_save():
            return
        self.txt_editor.config(state="normal")
        self.txt_editor.delete("1.0", tk.END)
        self.current_file = None
        self.is_new_file  = True
        self.is_editable  = True
        self.is_modified  = False
        self.lbl_modo.config(text="█ EDITABLE", fg=NEON_GREEN)
        self._update_line_numbers()
        self._update_title()
        self._set_status("NUEVO ARCHIVO — EDITOR HABILITADO >_")
        self._log("\n> NUEVO ARCHIVO CREADO.\n", "accent")

    def cmd_abrir(self):
        if self.is_modified and not self._ask_save():
            return
        path = filedialog.askopenfilename(
            title="Abrir archivo MicroC",
            filetypes=[("Archivos C", "*.c *.C"), ("Todos", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("ERROR", f"No se pudo abrir:\n{e}")
            return
        self.current_file = path
        self.is_new_file  = False
        self.is_editable  = False
        self.is_modified  = False
        self.txt_editor.config(state="normal")
        self.txt_editor.delete("1.0", tk.END)
        self.txt_editor.config(state="disabled")
        self.lbl_modo.config(text="█ CARGANDO...", fg=NEON_AMBER)
        self._log(f"\n> ABRIENDO: {path}\n", "info")
        self._type_text(content, on_done=self._after_open)

    def _after_open(self):
        self.txt_editor.config(state="disabled")
        self.lbl_modo.config(text="█ SOLO LECTURA", fg=NEON_PINK)
        self._update_line_numbers()
        self._highlight_syntax()
        self._update_token_count()
        self._update_title()
        self._set_status(f"CARGADO: {self.current_file}")
        self._log("> LISTO. USA [ EDITAR ] PARA MODIFICAR.\n", "ok")

    def _type_text(self, text, on_done=None, chunk=40, delay=4):
        self.txt_editor.config(state="normal")
        total = len(text)
        idx   = [0]
        def write():
            if idx[0] < total:
                end = min(idx[0] + chunk, total)
                self.txt_editor.insert(tk.END, text[idx[0]:end])
                self.txt_editor.see(tk.END)
                idx[0] = end
                self.after(delay, write)
            else:
                if on_done:
                    on_done()
        write()

    def cmd_guardar(self):
        content = self.txt_editor.get("1.0", tk.END)
        if self.is_new_file or not self.current_file:
            path = filedialog.asksaveasfilename(
                title="Guardar archivo MicroC",
                defaultextension=".c",
                filetypes=[("Archivos C", "*.c"), ("Todos", "*.*")])
            if not path:
                return
            self.current_file = path
            self.is_new_file  = False
        else:
            path = self.current_file
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            messagebox.showerror("ERROR", f"No se pudo guardar:\n{e}")
            return
        self.is_modified = False
        self._update_title()
        self._set_status(f"GUARDADO: {path}")
        self._log(f"\n> ARCHIVO GUARDADO: {path}\n", "ok")

    def cmd_editar(self):
        self.txt_editor.config(state="normal")
        self.is_editable = True
        self.lbl_modo.config(text="█ EDITABLE", fg=NEON_GREEN)
        self._set_status("MODO EDICIÓN ACTIVADO >_")
        self._log("\n> EDICIÓN HABILITADA.\n", "info")

    def cmd_compilar(self):
        content = self.txt_editor.get("1.0", tk.END).strip()
        if not content:
            self._log("\n> [ERROR] NO HAY CÓDIGO PARA COMPILAR.\n", "error")
            return
        self._log("\n" + "═" * 44 + "\n", "dim")
        self._log("▶ INICIANDO ANÁLISIS LÉXICO...\n", "accent")
        self.after(150, lambda: self._run_analysis(content))

    def _run_analysis(self, content):
        lines       = content.split("\n")
        errors      = []
        warns       = []
        brace_count = 0
        tokens      = re.findall(r'\b\w+\b|[+\-*/=<>!&|;,(){}]', content)

        for i, line in enumerate(lines, 1):
            s = line.strip()
            if not s or s.startswith("//"):
                continue
            brace_count += s.count("{") - s.count("}")
            if (s and
                not s.endswith(("{", "}", ";", ":")) and
                not s.startswith(("#", "//")) and
                not s.endswith("*/")):
                warns.append((i, f"Posible falta de ';'  →  {s[:45]}"))

        if brace_count != 0:
            errors.append(f"LLAVES DESBALANCEADAS: {abs(brace_count)} sin cerrar/abrir")

        kw_count  = sum(1 for t in tokens if t in KEYWORDS)
        num_count = sum(1 for t in tokens if re.match(r'^\d+$', t))

        self._log(f"\n  TOKENS TOTALES  : {len(tokens)}\n", "info")
        self._log(f"  PALABRAS CLAVE  : {kw_count}\n",      "info")
        self._log(f"  NÚMEROS         : {num_count}\n",      "info")
        self._log(f"  ADVERTENCIAS    : {len(warns)}\n",     "warn")
        self._log(f"  ERRORES         : {len(errors)}\n",    "error" if errors else "info")
        self._log("\n", "dim")

        if errors:
            self._log("[ ERRORES ]\n", "error")
            for e in errors:
                self._log(f"  ✗ {e}\n", "error")

        if warns:
            self._log("[ ADVERTENCIAS ]\n", "warn")
            for ln, msg in warns[:10]:
                self._log(f"  ⚠ Ln {ln:>3}: {msg}\n", "warn")
            if len(warns) > 10:
                self._log(f"  ... y {len(warns)-10} más.\n", "warn")

        if not errors and not warns:
            self._log("  ✔ SIN ERRORES DETECTADOS.\n", "ok")

        self._log("\n[ COMPILACIÓN COMPLETA EN PRÓXIMAS ENTREGAS ]\n", "dim")
        self._log("═" * 44 + "\n", "dim")

    def cmd_stats(self):
        content = self.txt_editor.get("1.0", tk.END)
        if not content.strip():
            self._log("\n> [STATS] Sin código para analizar.\n", "warn")
            return
        lines      = content.split("\n")
        total_ln   = len(lines)
        empty_ln   = sum(1 for l in lines if not l.strip())
        comment_ln = sum(1 for l in lines if l.strip().startswith("//"))
        code_ln    = total_ln - empty_ln - comment_ln
        tokens     = re.findall(r'\b\w+\b|[+\-*/=<>!&|;,(){}]', content)
        kw_used    = sorted(set(t for t in tokens if t in KEYWORDS))

        self._log("\n" + "═" * 44 + "\n", "dim")
        self._log("◈ ESTADÍSTICAS DEL CÓDIGO\n", "accent")
        self._log(f"  Líneas totales  : {total_ln}\n",  "info")
        self._log(f"  Líneas de código: {code_ln}\n",   "ok")
        self._log(f"  Líneas vacías   : {empty_ln}\n",  "dim")
        self._log(f"  Comentarios     : {comment_ln}\n","dim")
        self._log(f"  Caracteres      : {len(content)}\n", "info")
        self._log(f"  Palabras        : {len(content.split())}\n", "info")
        self._log(f"  Tokens totales  : {len(tokens)}\n","info")
        self._log(f"  Keywords usadas : {', '.join(kw_used) or 'ninguna'}\n", "warn")
        self._log("═" * 44 + "\n", "dim")

    def cmd_ayuda(self):
        win = tk.Toplevel(self)
        win.title("AYUDA — MicroC Compiler")
        win.geometry("520x480")
        win.configure(bg=BG_MAIN)
        win.resizable(False, False)
        tk.Frame(win, bg=NEON_GREEN, height=2).pack(fill="x")
        tk.Label(win, text="◈ AYUDA  —  MicroC Compiler v1.0",
                 bg=BG_MAIN, fg=NEON_GREEN,
                 font=("Courier New", 13, "bold")).pack(pady=(16, 4))
        tk.Frame(win, bg=DIM_GREEN, height=1).pack(fill="x", padx=20, pady=6)
        txt = tk.Text(win, bg=BG_PANEL, fg=TEXT_MAIN,
                      font=("Courier New", 10), relief="flat", bd=0,
                      padx=20, pady=10, state="normal", wrap="word")
        txt.pack(fill="both", expand=True, padx=10)
        txt.insert("1.0",
            "ATAJOS DE TECLADO:\n\n"
            "  Ctrl+N  →  Nuevo archivo\n"
            "  Ctrl+O  →  Abrir archivo .C\n"
            "  Ctrl+S  →  Guardar\n"
            "  Ctrl+E  →  Habilitar edición\n"
            "  Ctrl+T  →  Estadísticas del código\n"
            "  F5      →  Compilar / Análisis léxico\n\n"
            "FUNCIONES ÚNICAS:\n\n"
            "  • Resaltado de sintaxis en tiempo real\n"
            "  • Numeración de líneas sincronizada\n"
            "  • Contador de tokens en vivo\n"
            "  • Reloj en tiempo real\n"
            "  • Efecto typing al abrir archivos\n"
            "  • Estadísticas detalladas (Ctrl+T)\n"
            "  • Análisis léxico con reporte\n"
            "  • Auto-indentación al presionar Enter\n\n"
            "COLORES DE SINTAXIS:\n\n"
            "  CIAN   →  Palabras clave\n"
            "  ÁMBAR  →  Strings y operadores\n"
            "  ROSA   →  Números\n"
            "  VERDE  →  Directivas #include\n"
            "  GRIS   →  Comentarios\n\n"
            "Autómatas y Lenguajes  |  2026\n"
            "Ing. Baudilio Boteo  |  Univ. Mesoamericana"
        )
        txt.config(state="disabled")
        tk.Frame(win, bg=DIM_GREEN, height=1).pack(fill="x", padx=20, pady=6)
        tk.Button(win, text="[ CERRAR ]", command=win.destroy,
                  bg=NEON_GREEN, fg=BG_MAIN, relief="flat", bd=0,
                  font=("Courier New", 10, "bold"),
                  padx=20, pady=6, cursor="hand2").pack(pady=8)

    def cmd_acerca(self):
        messagebox.showinfo("Acerca de MicroC Compiler",
            "MicroC Compiler v1.0\nPre-Compilador\n\n"
            "Universidad Mesoamericana\n"
            "Autómatas y Lenguajes — 2026\n"
            "Ing. Baudilio Boteo\n\n"
            "Desarrollado en Python + Tkinter")

    def cmd_salir(self):
        if self.is_modified and not self._ask_save():
            return
        self._clock_running = False
        self.destroy()

    # ──────────────────────────────────────────────────────
    def _ask_save(self):
        r = messagebox.askyesnocancel("CAMBIOS SIN GUARDAR",
            "Tienes cambios sin guardar.\n¿Deseas guardar antes de continuar?")
        if r is None:
            return False
        if r:
            self.cmd_guardar()
        return True

    def _log(self, msg, style="ok"):
        self.txt_output.config(state="normal")
        self.txt_output.insert(tk.END, msg, style)
        self.txt_output.see(tk.END)
        self.txt_output.config(state="disabled")

    def _limpiar_consola(self):
        self.txt_output.config(state="normal")
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.config(state="disabled")
        self._log("> CONSOLA LIMPIADA.\n", "dim")

    def _set_status(self, text):
        self.lbl_status.config(text=f"  {text}")


# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = MicroCCompiler()
    app.mainloop()