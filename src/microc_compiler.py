"""
╔══════════════════════════════════════════════════════════╗
║       MicroC COMPILER  v2.0  — Analizador Léxico         ║
║       Universidad Mesoamericana  |  2026                 ║
║       Autómatas y Lenguajes  —  Ing. Baudilio Boteo      ║
╠══════════════════════════════════════════════════════════╣
║  Clases implementadas (diagrama UML):                    ║
║    • frmEditor       → Interfaz gráfica                  ║
║    • UnidadesLexicas → Tabla de tokens                   ║
║    • AnalizadorLexico→ Motor de análisis léxico          ║
╚══════════════════════════════════════════════════════════╝
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
DIM_GREEN  = "#00aa55"
TEXT_MAIN  = "#ccffcc"
TEXT_DIM   = "#336633"
CURSOR_CLR = "#00ff88"

KEYWORDS = [
    'int','float','char','void','return','if','else','while',
    'for','do','break','continue','printf','scanf','main',
    'include','define','struct','typedef','switch','case',
    'default','const','static','extern','sizeof','double',
    'long','short','unsigned','signed','enum','goto'
]


# ══════════════════════════════════════════════════════════
#  CLASE: UnidadesLexicas
#  Define las propiedades y funcionalidades de los objetos
#  para el uso de la tabla de símbolos del lenguaje
# ══════════════════════════════════════════════════════════
class UnidadesLexicas:

    def __init__(self):
        self.Palabra = {}
        self.Simbolo = {}
        self._cargar_palabras()
        self._cargar_simbolos()

    def _cargar_palabras(self):
        # Palabras reservadas C (tokens 1-32)
        reservadas = [
            "auto","break","case","char","const","continue","default",
            "do","double","else","enum","extern","float","for","goto",
            "if","int","long","register","return","short","signed",
            "sizeof","static","struct","switch","typedef","union",
            "unsigned","void","volatile","while"
        ]
        for i, p in enumerate(reservadas, 1):
            self.Palabra[p] = i

        # Directivas del preprocesador (tokens 100+)
        directivas = ["#include","#define","#ifdef","#ifndef",
                      "#endif","#if","#else","#elif","#pragma","#undef"]
        for i, d in enumerate(directivas, 100):
            self.Palabra[d] = i

        # Funciones stdio.h (tokens 200+)
        stdio = ["printf","scanf","fprintf","fscanf","sprintf","sscanf",
                 "fopen","fclose","fread","fwrite","fgets","fputs",
                 "getchar","putchar","gets","puts","feof","fflush"]
        for i, f in enumerate(stdio, 200):
            self.Palabra[f] = i

        # Funciones stdlib.h (tokens 250+)
        stdlib = ["malloc","calloc","realloc","free","exit","atoi",
                  "atof","atol","rand","srand","abs","system"]
        for i, f in enumerate(stdlib, 250):
            self.Palabra[f] = i

        # Funciones string.h (tokens 270+)
        string_h = ["strlen","strcpy","strcat","strcmp","strncpy",
                    "strncat","strncmp","strchr","strstr","strtok"]
        for i, f in enumerate(string_h, 270):
            self.Palabra[f] = i

        # Funciones math.h (tokens 290+)
        math_h = ["sqrt","pow","ceil","floor","sin","cos",
                  "tan","log","log10","exp"]
        for i, f in enumerate(math_h, 290):
            self.Palabra[f] = i

        # main es especial
        self.Palabra["main"] = 399

    def _cargar_simbolos(self):
        # Operadores aritméticos (40+)
        self.Simbolo["+"]  = 40
        self.Simbolo["-"]  = 41
        self.Simbolo["*"]  = 42
        self.Simbolo["/"]  = 43
        self.Simbolo["%"]  = 44
        # Asignación / incremental / decremental (50+)
        self.Simbolo["="]  = 50
        self.Simbolo["+="] = 51
        self.Simbolo["-="] = 52
        self.Simbolo["*="] = 53
        self.Simbolo["/="] = 54
        self.Simbolo["++"] = 55
        self.Simbolo["--"] = 56
        # Operadores relacionales (60+)
        self.Simbolo["=="] = 60
        self.Simbolo["!="] = 61
        self.Simbolo["<"]  = 62
        self.Simbolo[">"]  = 63
        self.Simbolo["<="] = 64
        self.Simbolo[">="] = 65
        # Operadores lógicos (70+)
        self.Simbolo["&&"] = 70
        self.Simbolo["||"] = 71
        self.Simbolo["!"]  = 72
        # Agrupación (75+)
        self.Simbolo["("]  = 75
        self.Simbolo[")"]  = 76
        self.Simbolo["{"]  = 77
        self.Simbolo["}"]  = 78
        self.Simbolo["["]  = 79
        self.Simbolo["]"]  = 80
        # Misceláneos (85+)
        self.Simbolo["\\n"] = 85
        self.Simbolo["\\t"] = 86
        self.Simbolo[";"]  = 92
        self.Simbolo[","]  = 93
        self.Simbolo["."]  = 94
        self.Simbolo[":"]  = 95
        self.Simbolo["?"]  = 96
        self.Simbolo["#"]  = 97
        self.Simbolo["&"]  = 98
        self.Simbolo["|"]  = 99

    def GetTokenPalabra(self, Lexema: str) -> int:
        """Retorna token de una palabra. 300 = identificador."""
        return self.Palabra.get(Lexema, 300)

    def GetTokenSimbolo(self, Lexema: str) -> int:
        """Retorna token de un símbolo. -1 = no encontrado."""
        return self.Simbolo.get(Lexema, -1)


# ══════════════════════════════════════════════════════════
#  CLASE: AnalizadorLexico
#  Define las propiedades y funcionalidades de los objetos
#  para el uso del analizador léxico
# ══════════════════════════════════════════════════════════
class AnalizadorLexico:

    def __init__(self):
        self.Lista = []
        self.cont  = 0
        self.Linea = 1

    def GetAlfabetoAlfanumerico(self, c: str) -> int:
        """Retorna 1 si el carácter es letra o guión bajo."""
        return 1 if (c.isalpha() or c == '_') else 0

    def GetAlfabetoNumero(self, c: str) -> int:
        """Retorna 1 si el carácter es dígito o punto."""
        return 1 if (c.isdigit() or c == '.') else 0

    def GetAlfabetoSimbolo(self, c: str) -> int:
        """Retorna 1 si el carácter es símbolo del lenguaje."""
        return 1 if c in set('=+-*/%<>!&|;,(){}[]:.?#^~') else 0

    def IdentificadorPalabraReservada(self, Archivo: str, UL: UnidadesLexicas):
        """
        Autómata para palabras reservadas e identificadores.
        Lee caracteres alfanuméricos y consulta la tabla.
        """
        lexema = ""
        while self.cont < len(Archivo):
            c = Archivo[self.cont]
            if c.isalnum() or c == '_':
                lexema += c
                self.cont += 1
            else:
                break

        token = UL.GetTokenPalabra(lexema)

        if token == 300:
            tipo = "IDENTIFICADOR"
        elif 1 <= token <= 32:
            tipo = "PALABRA_RESERVADA"
        elif 100 <= token <= 109:
            tipo = "DIRECTIVA"
        elif 200 <= token <= 299:
            tipo = "FUNCION_BIBLIOTECA"
        elif token == 399:
            tipo = "FUNCION_PRINCIPAL"
        else:
            tipo = "IDENTIFICADOR"

        self.Lista.append({
            "linea": self.Linea, "lexema": lexema,
            "token": token,      "tipo":   tipo
        })

    def EnteroReal(self, Archivo: str, UL: UnidadesLexicas):
        """
        Autómata para números enteros y reales.
        Lee dígitos y punto decimal.
        """
        lexema  = ""
        es_real = False

        while self.cont < len(Archivo):
            c = Archivo[self.cont]
            if c.isdigit():
                lexema += c
                self.cont += 1
            elif c == '.' and not es_real:
                es_real = True
                lexema += c
                self.cont += 1
            else:
                break

        if lexema:
            token = 401 if es_real else 400
            tipo  = "NUMERO_REAL" if es_real else "NUMERO_ENTERO"
            self.Lista.append({
                "linea": self.Linea, "lexema": lexema,
                "token": token,      "tipo":   tipo
            })

    def AutomataComentario(self, Archivo: str):
        """
        Autómata para comentarios de línea (//) y bloque (/* */).
        Los elimina del análisis y actualiza el contador de líneas.
        """
        self.cont += 1  # saltar el primer '/'
        if self.cont >= len(Archivo):
            return

        sig = Archivo[self.cont]

        if sig == '/':
            # Comentario de línea → ignorar hasta \n
            self.cont += 1
            while self.cont < len(Archivo) and Archivo[self.cont] != '\n':
                self.cont += 1
            self.Lista.append({
                "linea": self.Linea, "lexema": "//...",
                "token": 500,        "tipo":   "COMENTARIO_LINEA"
            })

        elif sig == '*':
            # Comentario de bloque → ignorar hasta */
            self.cont += 1
            linea_inicio = self.Linea
            while self.cont < len(Archivo) - 1:
                if Archivo[self.cont] == '\n':
                    self.Linea += 1
                if Archivo[self.cont] == '*' and Archivo[self.cont+1] == '/':
                    self.cont += 2
                    break
                self.cont += 1
            self.Lista.append({
                "linea": linea_inicio, "lexema": "/*...*/",
                "token": 501,          "tipo":   "COMENTARIO_BLOQUE"
            })
        else:
            # Era solo el operador '/'
            self.Lista.append({
                "linea": self.Linea, "lexema": "/",
                "token": 43,         "tipo":   "OPERADOR_ARITMETICO"
            })

    def AnalisisLexico(self, Archivo: str, UL: UnidadesLexicas) -> list:
        """
        Motor principal — árbol de decisión (while + ifs).
        Sigue el diagrama de flujo Figura III, IV, V del PDF.

        Flujo:
        1. Copiar TextBox1 en variable Archivo
        2. Instanciar AnalizadorLexico y UnidadesLexicas
        3. Recorrer Archivo carácter por carácter (while)
        4. Por cada carácter, decidir qué autómata llamar (ifs)
        5. Agregar token a Lista
        6. Retornar Lista → TextBox2
        """
        self.Lista = []
        self.cont  = 0
        self.Linea = 1

        # ── ÁRBOL DE DECISIÓN ──────────────────────────────
        while self.cont < len(Archivo):
            c = Archivo[self.cont]

            # Salto de línea → incrementar contador
            if c == '\n':
                self.Linea += 1
                self.cont  += 1
                continue

            # Espacios, tabuladores, retornos → eliminar
            if c in (' ', '\t', '\r'):
                self.cont += 1
                continue

            # Letra o guión bajo → IdentificadorPalabraReservada
            if self.GetAlfabetoAlfanumerico(c):
                self.IdentificadorPalabraReservada(Archivo, UL)
                continue

            # Directiva del preprocesador (#include, #define...)
            if c == '#':
                lexema = '#'
                self.cont += 1
                while self.cont < len(Archivo) and Archivo[self.cont].isalpha():
                    lexema += Archivo[self.cont]
                    self.cont += 1
                token = UL.GetTokenPalabra(lexema)
                self.Lista.append({
                    "linea": self.Linea, "lexema": lexema,
                    "token": token,      "tipo":   "DIRECTIVA"
                })
                continue

            # Número → EnteroReal
            if c.isdigit():
                self.EnteroReal(Archivo, UL)
                continue

            # Diagonal → posible comentario
            if c == '/':
                self.AutomataComentario(Archivo)
                continue

            # String entre comillas dobles
            if c == '"':
                lexema = '"'
                self.cont += 1
                while self.cont < len(Archivo) and Archivo[self.cont] != '"':
                    if Archivo[self.cont] == '\n':
                        self.Linea += 1
                    lexema += Archivo[self.cont]
                    self.cont += 1
                if self.cont < len(Archivo):
                    lexema += '"'
                    self.cont += 1
                self.Lista.append({
                    "linea": self.Linea, "lexema": lexema,
                    "token": 502,        "tipo":   "CADENA"
                })
                continue

            # Carácter entre comillas simples
            if c == "'":
                lexema = "'"
                self.cont += 1
                while self.cont < len(Archivo) and Archivo[self.cont] != "'":
                    lexema += Archivo[self.cont]
                    self.cont += 1
                if self.cont < len(Archivo):
                    lexema += "'"
                    self.cont += 1
                self.Lista.append({
                    "linea": self.Linea, "lexema": lexema,
                    "token": 503,        "tipo":   "CARACTER"
                })
                continue

            # Símbolo → revisar si es de 2 caracteres primero
            if self.GetAlfabetoSimbolo(c):
                lexema = c
                if self.cont + 1 < len(Archivo):
                    dos = c + Archivo[self.cont + 1]
                    if dos in ('==','!=','<=','>=','&&','||',
                               '++','--','+=','-=','*=','/=','->'):
                        lexema = dos
                        self.cont += 2
                    else:
                        self.cont += 1
                else:
                    self.cont += 1

                token = UL.GetTokenSimbolo(lexema)
                if token == -1:
                    tipo = "SIMBOLO_NO_ENCONTRADO"
                elif token in range(40, 45):
                    tipo = "OPERADOR_ARITMETICO"
                elif token in range(50, 57):
                    tipo = "ASIGNACION"
                elif token in range(60, 66):
                    tipo = "OPERADOR_RELACIONAL"
                elif token in range(70, 73):
                    tipo = "OPERADOR_LOGICO"
                elif token in range(75, 81):
                    tipo = "AGRUPACION"
                else:
                    tipo = "SIMBOLO"

                self.Lista.append({
                    "linea": self.Linea, "lexema": lexema,
                    "token": token,      "tipo":   tipo
                })
                continue

            # Carácter no reconocido
            self.Lista.append({
                "linea": self.Linea, "lexema": c,
                "token": -1,         "tipo":   "DESCONOCIDO"
            })
            self.cont += 1

        return self.Lista


# ══════════════════════════════════════════════════════════
#  CLASE: frmEditor
#  Define los objetos para el frame / visualización gráfica
#  del compilador con los botones mínimos para su funcionamiento
# ══════════════════════════════════════════════════════════
class frmEditor(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("MicroC COMPILER v2.0 — Analizador Léxico")
        self.geometry("1280x760")
        self.configure(bg=BG_MAIN)
        self.minsize(900, 600)

        self.Archivo        = ""
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

        make_menu("[ ARCHIVOS ]", [
            ("  >> NUEVO              Ctrl+N",    self.OpcNuevo_Click),
            ("  >> ABRIR              Ctrl+O",    self.OpcAbrir_Click),
            ("  >> GUARDAR            Ctrl+S",    self.OpcGuardar_Click),
            ("  >> GUARDAR COMO  Ctrl+Mayús+S",   self.OpcGuardarComo_Click),
            "---",
            ("  >> SALIR",                        self.OpcSalir_Click),
        ])
        make_menu("[ EDITAR ]", [
            ("  >> HABILITAR EDICIÓN  Ctrl+E",    self.cmd_editar),
            ("  >> DESHACER           Ctrl+Z",    lambda: self.txt_editor.edit_undo()),
            ("  >> REHACER            Ctrl+Y",    lambda: self.txt_editor.edit_redo()),
        ])
        make_menu("[ COMPILAR ]", [
            ("  >> COMPILAR           F5",        self.compilarToolStripMenuItem_Click),
            ("  >> LIMPIAR CONSOLA",              self._limpiar_consola),
            ("  >> ESTADÍSTICAS       Ctrl+T",    self.cmd_stats),
        ])
        make_menu("[ AYUDA ]", [
            ("  >> AYUDA / ATAJOS",               self.cmd_ayuda),
            ("  >> ACERCA DE",                    self.cmd_acerca),
        ])

        # HEADER
        header = tk.Frame(self, bg=BG_HEADER, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="◈ MicroC COMPILER",
                 bg=BG_HEADER, fg=NEON_GREEN,
                 font=("Courier New", 16, "bold")).pack(side="left", padx=16)
        tk.Label(header, text="ANALIZADOR LÉXICO  |  UNIV. MESOAMERICANA  |  2026",
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
            ("[ NUEVO ]",       self.OpcNuevo_Click,                 NEON_GREEN),
            ("[ ABRIR ]",       self.OpcAbrir_Click,                 NEON_GREEN),
            ("[ GUARDAR ]",     self.OpcGuardar_Click,               NEON_GREEN),
            ("[ GUARDAR COMO ]",self.OpcGuardarComo_Click,           NEON_GREEN),
            ("[ EDITAR ]",      self.cmd_editar,                     NEON_AMBER),
            ("[ COMPILAR ]",    self.compilarToolStripMenuItem_Click, NEON_CYAN),
            ("[ STATS ]",       self.cmd_stats,                      NEON_PINK),
            ("[ AYUDA ]",       self.cmd_ayuda,                      DIM_GREEN),
            ("[ SALIR ]",       self.OpcSalir_Click,                 NEON_PINK),
        ]
        for text, cmd, color in btns:
            b = tk.Button(toolbar, text=text, command=cmd,
                          bg=BG_PANEL, fg=color, relief="flat", bd=0,
                          font=("Courier New", 8, "bold"),
                          padx=8, pady=8, cursor="hand2",
                          activebackground=color, activeforeground=BG_MAIN)
            b.pack(side="left", padx=1)
            b.bind("<Enter>", lambda e, btn=b, c=color: btn.config(bg=c, fg=BG_MAIN))
            b.bind("<Leave>", lambda e, btn=b, c=color: btn.config(bg=BG_PANEL, fg=c))

        tk.Frame(self, bg=DIM_GREEN, height=1).pack(fill="x")

        # ÁREA PRINCIPAL
        main = tk.Frame(self, bg=BG_MAIN)
        main.pack(fill="both", expand=True)

        # PANEL IZQUIERDO — TextBox1
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

        # PANEL DERECHO — TextBox2
        right = tk.Frame(main, bg=BG_MAIN, width=460)
        right.pack(side="right", fill="both")
        right.pack_propagate(False)

        con_hdr = tk.Frame(right, bg=BG_HEADER, height=28)
        con_hdr.pack(fill="x")
        con_hdr.pack_propagate(False)
        tk.Label(con_hdr, text=" ◈ TOKENS  [ TextBox2 ]",
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

        self.txt_output.tag_configure("ok",        foreground=NEON_GREEN)
        self.txt_output.tag_configure("error",     foreground=NEON_PINK)
        self.txt_output.tag_configure("warn",      foreground=NEON_AMBER)
        self.txt_output.tag_configure("info",      foreground=NEON_CYAN)
        self.txt_output.tag_configure("dim",       foreground=DIM_GREEN)
        self.txt_output.tag_configure("accent",    foreground=NEON_GREEN, font=("Courier New", 11, "bold"))
        self.txt_output.tag_configure("kw",        foreground=NEON_CYAN)
        self.txt_output.tag_configure("num",       foreground=NEON_PINK)
        self.txt_output.tag_configure("sym",       foreground=NEON_AMBER)
        self.txt_output.tag_configure("id",        foreground=TEXT_MAIN)
        self.txt_output.tag_configure("err_tok",   foreground=NEON_PINK,  font=("Courier New", 11, "bold"))
        self.txt_output.tag_configure("com_tag",   foreground=TEXT_DIM)

    # ──────────────────────────────────────────────────────
    def _bind_events(self):
        self.bind("<Control-n>", lambda e: self.OpcNuevo_Click())
        self.bind("<Control-o>", lambda e: self.OpcAbrir_Click())
        self.bind("<Control-s>", lambda e: self.OpcGuardar_Click())
        self.bind("<Control-S>", lambda e: self.OpcGuardarComo_Click())
        self.bind("<Control-e>", lambda e: self.cmd_editar())
        self.bind("<Control-t>", lambda e: self.cmd_stats())
        self.bind("<F5>",        lambda e: self.compilarToolStripMenuItem_Click())
        self.protocol("WM_DELETE_WINDOW", self.OpcSalir_Click)
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
        self.title(f"MicroC COMPILER v2.0  —  {name}{mod}")
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
            ("║   MicroC COMPILER  v2.0                  ║\n", "accent"),
            ("║   Analizador Léxico  —  2026             ║\n", "accent"),
            ("╚══════════════════════════════════════════╝\n", "accent"),
            ("\n", "dim"),
            ("[ OK ] Cargando UnidadesLexicas...\n",   "ok"),
            ("[ OK ] Cargando AnalizadorLexico...\n",  "ok"),
            ("[ OK ] Tabla de tokens lista\n",         "ok"),
            ("[ OK ] Resaltado de sintaxis activo\n",  "ok"),
            ("\n", "dim"),
            ("─────────────────────────────────────────\n", "dim"),
            (" F5 = Compilar  |  Ctrl+T = Stats\n",       "info"),
            ("─────────────────────────────────────────\n", "dim"),
            ("\n", "dim"),
            (" > LISTO. ESPERANDO CÓDIGO...\n",           "accent"),
        ]
        def show(i=0):
            if i < len(msgs):
                self._log(msgs[i][0], msgs[i][1])
                self.after(60, lambda: show(i + 1))
        self.after(300, lambda: show())

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
    #  FUNCIONES PRINCIPALES (nombres según diagrama UML)
    # ──────────────────────────────────────────────────────

    def OpcNuevo_Click(self):
        if self.is_modified and not self._ask_save():
            return
        self.txt_editor.config(state="normal")
        self.txt_editor.delete("1.0", tk.END)
        self.Archivo      = ""
        self.current_file = None
        self.is_new_file  = True
        self.is_editable  = True
        self.is_modified  = False
        self.lbl_modo.config(text="█ EDITABLE", fg=NEON_GREEN)
        self._update_line_numbers()
        self._update_title()
        self._set_status("NUEVO ARCHIVO — EDITOR HABILITADO >_")
        self._log("\n> NUEVO ARCHIVO CREADO.\n", "accent")

    def OpcAbrir_Click(self):
        if self.is_modified and not self._ask_save():
            return
        path = filedialog.askopenfilename(
            title="Abrir archivo MicroC",
            filetypes=[("Archivos C", "*.c *.C *.cpp"), ("Todos", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("ERROR", f"No se pudo abrir:\n{e}")
            return
        self.Archivo      = content
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
        self.Archivo = self.txt_editor.get("1.0", tk.END)
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

    def OpcGuardar_Click(self):
        content = self.txt_editor.get("1.0", tk.END)
        if self.is_new_file or not self.current_file:
            self.OpcGuardarComo_Click()
            return
        try:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            messagebox.showerror("ERROR", f"No se pudo guardar:\n{e}")
            return
        self.Archivo     = content
        self.is_modified = False
        self._update_title()
        self._set_status(f"GUARDADO: {self.current_file}")
        self._log(f"\n> GUARDADO: {self.current_file}\n", "ok")

    def OpcGuardarComo_Click(self):
        path = filedialog.asksaveasfilename(
            title="Guardar como",
            defaultextension=".c",
            filetypes=[("Archivos C", "*.c"), ("Todos", "*.*")])
        if not path:
            return
        content = self.txt_editor.get("1.0", tk.END)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            messagebox.showerror("ERROR", f"No se pudo guardar:\n{e}")
            return
        self.Archivo      = content
        self.current_file = path
        self.is_new_file  = False
        self.is_modified  = False
        self._update_title()
        self._set_status(f"GUARDADO COMO: {path}")
        self._log(f"\n> GUARDADO COMO: {path}\n", "ok")

    def OpcSalir_Click(self):
        if self.is_modified and not self._ask_save():
            return
        self._clock_running = False
        self.destroy()

    def cmd_editar(self):
        self.txt_editor.config(state="normal")
        self.is_editable = True
        self.lbl_modo.config(text="█ EDITABLE", fg=NEON_GREEN)
        self._set_status("MODO EDICIÓN ACTIVADO >_")
        self._log("\n> EDICIÓN HABILITADA.\n", "info")

    def compilarToolStripMenuItem_Click(self):
        """
        Flujo según diagrama Figura III:
        1. Copiar TextBox1 en variable Archivo
        2. Instanciar AnalizadorLexico (AL) y UnidadesLexicas (UL)
        3. Llamar AL.AnalisisLexico(Archivo)
        4. Guardar en ListToken
        5. Escribir en TextBox2
        """
        # Paso 1
        self.Archivo = self.txt_editor.get("1.0", tk.END).strip()
        if not self.Archivo:
            self._log("\n> [ERROR] NO HAY CÓDIGO PARA COMPILAR.\n", "error")
            return

        self._limpiar_consola()
        self._log("═" * 46 + "\n", "dim")
        self._log("▶ INICIANDO ANÁLISIS LÉXICO...\n", "accent")
        self._log("═" * 46 + "\n", "dim")

        # Paso 2
        AL = AnalizadorLexico()
        UL = UnidadesLexicas()

        # Pasos 3 y 4
        ListToken = AL.AnalisisLexico(self.Archivo, UL)

        # Paso 5
        self.after(100, lambda: self._mostrar_tokens(ListToken))

    def _mostrar_tokens(self, ListToken: list):
        """Escribe la tabla en TextBox2 — formato Figura V del PDF."""
        self._log(f"\n{'LÍNEA':<10}{'LEXEMA':<22}{'TOKEN':<10}TIPO\n", "info")
        self._log("─" * 55 + "\n", "dim")

        errores = 0
        for t in ListToken:
            fila = (f"Linea: {t['linea']:<6}"
                    f"Lexema: {t['lexema']:<18}"
                    f"Token: {t['token']:<8}"
                    f"{t['tipo']}\n")

            if t["token"] == -1:
                self._log(fila, "err_tok")
                errores += 1
            elif t["tipo"] in ("COMENTARIO_LINEA","COMENTARIO_BLOQUE"):
                self._log(fila, "com_tag")
            elif t["tipo"] in ("PALABRA_RESERVADA","DIRECTIVA",
                               "FUNCION_BIBLIOTECA","FUNCION_PRINCIPAL"):
                self._log(fila, "kw")
            elif t["tipo"] in ("NUMERO_ENTERO","NUMERO_REAL"):
                self._log(fila, "num")
            elif t["tipo"] == "IDENTIFICADOR":
                self._log(fila, "id")
            else:
                self._log(fila, "sym")

        self._log("─" * 55 + "\n", "dim")
        self._log(f"\n  TOTAL TOKENS    : {len(ListToken)}\n", "info")
        self._log(f"  ERRORES LÉXICOS : {errores}\n",
                  "error" if errores else "info")

        if errores == 0:
            self._log("\n  ✔ ANÁLISIS LÉXICO COMPLETADO SIN ERRORES.\n", "ok")
        else:
            self._log(f"\n  ✗ {errores} SÍMBOLO(S) NO RECONOCIDO(S).\n", "error")

        self._log("═" * 46 + "\n", "dim")
        self.lbl_tokens.config(text=f"TOKENS: {len(ListToken)}")
        self._set_status(f"COMPILACIÓN COMPLETA — {len(ListToken)} tokens")

    def cmd_stats(self):
        content = self.txt_editor.get("1.0", tk.END)
        if not content.strip():
            self._log("\n> [STATS] Sin código para analizar.\n", "warn")
            return
        AL = AnalizadorLexico()
        UL = UnidadesLexicas()
        ListToken = AL.AnalisisLexico(content, UL)
        tipos = {}
        for t in ListToken:
            tipos[t["tipo"]] = tipos.get(t["tipo"], 0) + 1
        lines      = content.split("\n")
        total_ln   = len(lines)
        empty_ln   = sum(1 for l in lines if not l.strip())
        comment_ln = sum(1 for l in lines if l.strip().startswith("//"))
        code_ln    = total_ln - empty_ln - comment_ln

        self._log("\n" + "═" * 46 + "\n", "dim")
        self._log("◈ ESTADÍSTICAS DEL CÓDIGO\n", "accent")
        self._log(f"  Líneas totales       : {total_ln}\n",      "info")
        self._log(f"  Líneas de código     : {code_ln}\n",       "ok")
        self._log(f"  Líneas vacías        : {empty_ln}\n",      "dim")
        self._log(f"  Comentarios          : {comment_ln}\n",    "dim")
        self._log(f"  Tokens totales       : {len(ListToken)}\n","info")
        self._log("\n  DISTRIBUCIÓN:\n", "info")
        for tipo, cant in sorted(tipos.items(), key=lambda x: -x[1]):
            self._log(f"    {tipo:<28}: {cant}\n", "dim")
        self._log("═" * 46 + "\n", "dim")

    def cmd_ayuda(self):
        win = tk.Toplevel(self)
        win.title("AYUDA — MicroC Compiler v2.0")
        win.geometry("540x520")
        win.configure(bg=BG_MAIN)
        win.resizable(False, False)
        tk.Frame(win, bg=NEON_GREEN, height=2).pack(fill="x")
        tk.Label(win, text="◈ AYUDA  —  MicroC Compiler v2.0",
                 bg=BG_MAIN, fg=NEON_GREEN,
                 font=("Courier New", 13, "bold")).pack(pady=(16, 4))
        tk.Frame(win, bg=DIM_GREEN, height=1).pack(fill="x", padx=20, pady=6)
        txt = tk.Text(win, bg=BG_PANEL, fg=TEXT_MAIN,
                      font=("Courier New", 10), relief="flat", bd=0,
                      padx=20, pady=10, state="normal", wrap="word")
        txt.pack(fill="both", expand=True, padx=10)
        txt.insert("1.0",
            "ATAJOS DE TECLADO:\n\n"
            "  Ctrl+N        →  Nuevo archivo\n"
            "  Ctrl+O        →  Abrir archivo .C\n"
            "  Ctrl+S        →  Guardar\n"
            "  Ctrl+Mayús+S  →  Guardar Como\n"
            "  Ctrl+E        →  Habilitar edición\n"
            "  Ctrl+T        →  Estadísticas\n"
            "  F5            →  Compilar / Análisis léxico\n\n"
            "CLASES IMPLEMENTADAS (diagrama UML):\n\n"
            "  frmEditor        →  Interfaz gráfica\n"
            "  UnidadesLexicas  →  Tabla de tokens\n"
            "  AnalizadorLexico →  Motor léxico\n\n"
            "COLORES EN TEXTBOX2:\n\n"
            "  CIAN    →  Palabras reservadas / funciones\n"
            "  ÁMBAR   →  Símbolos y operadores\n"
            "  ROSA    →  Números enteros y reales\n"
            "  BLANCO  →  Identificadores\n"
            "  GRIS    →  Comentarios\n"
            "  ROJO    →  Símbolo no encontrado\n\n"
            "Autómatas y Lenguajes  |  2026\n"
            "Ing. Baudilio Boteo  |  Univ. Mesoamericana\n"
            "Andrea Gonzalez  |  202425508"
        )
        txt.config(state="disabled")
        tk.Frame(win, bg=DIM_GREEN, height=1).pack(fill="x", padx=20, pady=6)
        tk.Button(win, text="[ CERRAR ]", command=win.destroy,
                  bg=NEON_GREEN, fg=BG_MAIN, relief="flat", bd=0,
                  font=("Courier New", 10, "bold"),
                  padx=20, pady=6, cursor="hand2").pack(pady=8)

    def cmd_acerca(self):
        messagebox.showinfo("Acerca de MicroC Compiler",
            "MicroC Compiler v2.0\nAnalizador Léxico\n\n"
            "Clases: frmEditor, AnalizadorLexico, UnidadesLexicas\n\n"
            "Universidad Mesoamericana\n"
            "Autómatas y Lenguajes — 2026\n"
            "Ing. Baudilio Boteo\n\n"
            "Desarrollado en Python + Tkinter\n"
            "Andrea Gonzalez — 202425508")

    # ──────────────────────────────────────────────────────
    def _ask_save(self):
        r = messagebox.askyesnocancel("CAMBIOS SIN GUARDAR",
            "Tenés cambios sin guardar.\n¿Guardás antes de continuar?")
        if r is None:
            return False
        if r:
            self.OpcGuardar_Click()
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
    app = frmEditor()
    app.mainloop()