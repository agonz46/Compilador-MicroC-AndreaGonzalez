# Manual de usuario — MicroC Compiler v2.0

Esta es la segunda versión del compilador MicroC. Ya tiene el analizador léxico completo, así que cuando compilás te genera una tabla con todos los tokens que encontró en el código.

---

## Cómo se ve el programa

```
┌─────────────────────────────────────────────────────────┐
│  ◈ MicroC COMPILER    ANALIZADOR LÉXICO  |  2026  ⬡ hora│
├─────────────────────────────────────────────────────────┤
│ [NUEVO][ABRIR][GUARDAR][GUARDAR COMO][EDITAR][COMPILAR] │
├──────────────────────────┬──────────────────────────────┤
│ ◈ EDITOR [TextBox1]      │ ◈ TOKENS [TextBox2]          │
│                          │                              │
│  1  │ #include <stdio.h> │ Linea: 1  Lexema: #include  │
│  2  │ int main() {       │ Token: 100  DIRECTIVA        │
│  3  │     int a = 5;     │ Linea: 2  Lexema: int        │
│  4  │ }                  │ Token: 17  PALABRA_RESERVADA │
├──────────────────────────┴──────────────────────────────┤
│  SISTEMA LISTO  LÍNEAS: 4   LN:1 COL:1   TOKENS: 12    │
└─────────────────────────────────────────────────────────┘
```

---

## Los botones

**[ NUEVO ] — Ctrl+N**  
Limpia el editor y lo pone en modo editable. El indicador arriba a la derecha cambia a verde y dice EDITABLE.

**[ ABRIR ] — Ctrl+O**  
Abre el explorador para buscar un archivo `.c`. Cuando lo cargás el texto aparece con una animación de typing. Queda en modo solo lectura.

**[ GUARDAR ] — Ctrl+S**  
Si el archivo ya tiene nombre lo sobreescribe. Si es nuevo te pide dónde guardarlo.

**[ GUARDAR COMO ] — Ctrl+Mayús+S**  
Siempre abre el explorador para elegir una nueva ubicación, aunque el archivo ya exista.

**[ EDITAR ] — Ctrl+E**  
Habilita la edición del archivo que abriste. El indicador cambia a EDITABLE.

**[ COMPILAR ] — F5**  
Acá está lo nuevo. Toma el código del editor y lo analiza carácter por carácter. En la consola aparece una tabla con cada token que encontró, con su número de línea, el lexema y el token asignado. Los errores léxicos aparecen en rojo.

**[ STATS ] — Ctrl+T**  
Muestra estadísticas del código: cuántas líneas hay, cuántos tokens, cómo están distribuidos por tipo.

**[ AYUDA ]**  
Abre una ventana con los atajos y las clases implementadas.

**[ SALIR ]**  
Cierra el programa. Si tenés cambios sin guardar te pregunta antes.

---

## La tabla de tokens

Cuando compilás, la consola muestra algo así:

```
LÍNEA     LEXEMA                TOKEN     TIPO
───────────────────────────────────────────────────────
Linea: 1  Lexema: #include      Token: 100  DIRECTIVA
Linea: 3  Lexema: int           Token: 17   PALABRA_RESERVADA
Linea: 3  Lexema: main          Token: 399  FUNCION_PRINCIPAL
Linea: 3  Lexema: (             Token: 75   AGRUPACION
Linea: 4  Lexema: a             Token: 300  IDENTIFICADOR
Linea: 4  Lexema: =             Token: 50   ASIGNACION
Linea: 4  Lexema: 5             Token: 400  NUMERO_ENTERO
Linea: 17 Lexema: @             Token: -1   SIMBOLO_NO_ENCONTRADO
```

Los colores en la consola:
- **Cian** → palabras reservadas y funciones de biblioteca
- **Rosa** → números enteros y reales
- **Ámbar** → operadores y símbolos
- **Blanco** → identificadores
- **Gris** → comentarios
- **Rojo** → error léxico (símbolo no reconocido)

---

## Atajos de teclado

| Atajo | Qué hace |
|-------|---------|
| Ctrl+N | Nuevo archivo |
| Ctrl+O | Abrir archivo |
| Ctrl+S | Guardar |
| Ctrl+Mayús+S | Guardar Como |
| Ctrl+E | Habilitar edición |
| Ctrl+T | Estadísticas |
| Ctrl+Z | Deshacer |
| Ctrl+Y | Rehacer |
| F5 | Compilar / Análisis léxico |

---

## Cómo probar que funciona

Abrí el programa, dale a Nuevo, pegá esto y presioná F5:

```c
#include <stdio.h>

int main() {
    int a = 5;
    float b = 3.14;
    // comentario
    printf("hola");
    int @ = 10;
    return 0;
}
```

Deberías ver todos los tokens bien clasificados y el `@` en rojo como error léxico.

---

## La barra de estado

```
SISTEMA LISTO >_     LÍNEAS: 10     LN:3  COL:5     TOKENS: 34
```

- Izquierda: mensaje del sistema
- LÍNEAS: cuántas líneas tiene el archivo
- LN/COL: posición del cursor
- TOKENS: se actualiza solo mientras escribís