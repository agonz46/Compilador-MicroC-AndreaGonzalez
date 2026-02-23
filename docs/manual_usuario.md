Manual de usuario — MicroC Compiler

Acá explico cómo usar el programa por si alguien lo descarga y no sabe por dónde empezar.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Cómo se ve cuando lo abrís

La ventana está dividida en dos partes. A la izquierda está el editor donde escribís o cargás el código, y a la derecha está la consola que te va mostrando mensajes de lo que va pasando. Arriba hay una barra con todos los botones y abajo una barra chica que te dice en qué línea y columna está el cursor y cuántos tokens tiene el código.

Cuando lo abrís por primera vez la consola hace una animación de arranque y te dice que el sistema está listo.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Los botones y qué hace cada uno

NUEVO — Limpia el editor y te lo deja listo para escribir. El indicador de arriba cambia a verde y dice EDITABLE.

ABRIR — Abre el explorador de archivos para que busques un ".c". Cuando lo seleccionás el texto aparece con una animación de typing, como si se estuviera escribiendo solo. El archivo queda en modo solo lectura para que no lo edites de casualidad.

GUARDAR — Si el archivo es nuevo te pregunta dónde guardarlo. Si ya lo habías guardado antes lo sobreescribe sin preguntar. Cuando hay cambios sin guardar el título de la ventana tiene un "[*]" para que te acordés.

EDITAR — Si abriste un archivo y querés modificarlo, dale a este botón. El indicador cambia a verde y ya podés escribir.

COMPILAR (o F5) — Hace un análisis básico del código y te muestra en la consola cuántos tokens encontró, si hay palabras clave, si falta algún punto y coma o si las llaves están desbalanceadas. La compilación completa viene en la siguiente entrega.

STATS (o Ctrl+T) — Te muestra un resumen del código: cuántas líneas tiene, cuántas están vacías, cuántos son comentarios, cuántos caracteres, tokens y qué keywords usaste.

AYUDA — Abre una ventanita con los atajos de teclado y un resumen de las funciones.

SALIR — Cierra el programa. Si tenés cambios sin guardar te pregunta si querés guardar antes de cerrar.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Atajos de teclado

Ctrl + N: Nuevo archivo
Ctrl + O: Abrir archivo
Ctrl + S: Guardar
Ctrl + E: Habilitar edición
Ctrl + T: Ver estadísticas
Ctrl + Z: Deshacer
Ctrl + Y: Rehacer
F5: Compilar

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Los colores del editor

Cuando escribís código el editor lo colorea automáticamente:

- Las palabras clave como "int", "return", "if" se ponen en cian
- Los textos entre comillas "así" se ponen en ámbar
- Los números se ponen en rosa
- Las directivas como "#include" se ponen en verde brillante
- Los comentarios "// así" se ponen en gris oscuro

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

La barra de abajo

SISTEMA LISTO >_     LÍNEAS: 10     LN:3  COL:5     TOKENS: 34

- El mensaje de la izquierda cambia según lo que estás haciendo
- LÍNEAS te dice cuántas líneas tiene el archivo
- LN y COL te dicen dónde está el cursor
- TOKENS se actualiza solo mientras escribís

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Una cosa útil

Cuando estás dentro de un bloque con llaves "{}" y presionás Enter, el editor te pone automáticamente la indentación del nivel que corresponde. Si la línea anterior terminaba con "{" te agrega 4 espacios más.