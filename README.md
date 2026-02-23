# ◈ MicroC Compiler — Pre-Compilador

```
╔══════════════════════════════════════════════════════════╗
║          MicroC COMPILER  v1.0  — Pre-Compilador         ║
║          Universidad Mesoamericana  |  2026              ║
╚══════════════════════════════════════════════════════════╝
```

---

## 📋 Portada

| Campo | Detalle |
|-------|---------|
| **Nombre completo** | _(Tu nombre aquí)_ |
| **Número de carné** | _(Tu carné aquí)_ |
| **Curso** | Autómatas y Lenguajes |
| **Proyecto** | Compilador MicroC — Pre-Compilador |
| **Catedrático** | Ing. Baudilio Boteo |
| **Universidad** | Universidad Mesoamericana |
| **Año** | 2026 |

---

## 📌 Descripción del Proyecto

**MicroC Compiler** es una aplicación de escritorio con estética **retro-terminal / cyberpunk** que simula la interfaz de un compilador para el lenguaje **MicroC** (subconjunto de C). Esta primera entrega es el **Pre-Compilador**, con interfaz completa, manejo de archivos y análisis léxico básico.

### Funciones implementadas

| Función | Descripción |
|---------|-------------|
| **Nuevo** | Crea archivo nuevo y habilita el editor |
| **Abrir** | Carga un `.C` en modo solo lectura con efecto typing |
| **Guardar** | Guarda con diálogo (nuevo) o sobreescribe (existente) |
| **Editar** | Habilita la edición del archivo abierto |
| **Compilar (F5)** | Análisis léxico con reporte detallado |
| **Stats (Ctrl+T)** | Estadísticas del código en tiempo real |
| **Ayuda** | Ventana con atajos y documentación |
| **Salir** | Cierra con verificación de cambios |

### ✦ Extras sobre los requisitos mínimos

- 🎨 **Tema retro-terminal cyberpunk** — fondo negro + neón verde/cian/ámbar
- ⚡ **Resaltado de sintaxis en tiempo real** — keywords, strings, comentarios, números
- 🔢 **Numeración de líneas** sincronizada con scroll
- 📊 **Contador de tokens léxicos en vivo** en la barra de estado
- 🕐 **Reloj en tiempo real** en la barra superior
- ⌨️ **Efecto typing** animado al abrir archivos
- 📈 **Estadísticas del código** (Ctrl+T): líneas, tokens, keywords usadas
- 🔍 **Análisis léxico detallado** al compilar: tokens, errores, advertencias
- 🔧 **Auto-indentación** al presionar Enter
- ↩️ **Deshacer/Rehacer** (Ctrl+Z / Ctrl+Y)
- 💾 **Indicador de cambios** `[*]` en el título de la ventana

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Uso |
|-----------|-----|
| **Python 3.10+** | Lenguaje principal |
| **Tkinter** | Interfaz gráfica (incluida en Python) |
| **re (regex)** | Resaltado de sintaxis y análisis léxico |
| **threading** | Reloj en tiempo real sin bloquear la UI |
| **os / datetime** | Manejo de archivos y tiempo |

> No requiere instalar librerías externas.

---

## ▶️ Instrucciones de Ejecución

### Requisitos
- Python 3.10 o superior

### Ejecutar
```bash
# Clona el repositorio
git clone https://github.com/TuUsuario/Compilador-MicroC-TuNombreApellido.git

# Entra a la carpeta
cd Compilador-MicroC-TuNombreApellido

# Ejecuta
python src/microc_compiler.py
```

### Crear ejecutable .exe (opcional)
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name MicroCCompiler src/microc_compiler.py
```
El `.exe` quedará en la carpeta `dist/`.

---

## 📸 Capturas de Pantalla

> _(Agrega tus capturas aquí después de ejecutar el programa)_

Guárdalas en `docs/screenshots/` con nombres como:
- `pantalla_principal.png`
- `abrir_archivo.png`
- `compilar.png`
- `stats.png`

---

## 🎬 Video Demostrativo

> 🔗 [Ver video](#) ← _(Reemplaza con tu enlace real de Drive o YouTube)_

---

## 📁 Estructura del Repositorio

```
Compilador-MicroC-TuNombreApellido/
│
├── src/
│   └── microc_compiler.py    ← Código fuente principal
│
├── assets/                   ← Recursos (íconos, imágenes)
│
├── docs/
│   ├── manual_usuario.md     ← Manual de usuario
│   └── screenshots/          ← Capturas de pantalla
│
├── test/
│   └── prueba.c              ← Archivo de prueba
│
└── README.md
```

---

## ⌨️ Atajos de Teclado

| Atajo | Función |
|-------|---------|
| `Ctrl + N` | Nuevo archivo |
| `Ctrl + O` | Abrir archivo |
| `Ctrl + S` | Guardar |
| `Ctrl + E` | Habilitar edición |
| `Ctrl + T` | Estadísticas del código |
| `Ctrl + Z` | Deshacer |
| `Ctrl + Y` | Rehacer |
| `F5` | Compilar / Análisis léxico |

---

## 🏷️ Release

- **Tag:** `v1.0-precompilador`
- **Estado:** Pre-Compilador funcional con análisis léxico básico
- **Próxima entrega:** Analizador sintáctico completo

---

## 📜 Licencia

Proyecto académico — Universidad Mesoamericana 2026.