# Proyecto Nand2Tetris – Traductor de la Máquina Virtual (VM Translator)

## Descripción general
Este proyecto implementa un traductor del lenguaje de Máquina Virtual (VM) al lenguaje ensamblador **Hack**, siguiendo las especificaciones del curso *Nand2Tetris* ("Construyendo una computadora moderna desde cero").  
Permite convertir archivos `.vm` o carpetas enteras (módulos múltiples) generando como salida un único archivo `.asm` listo para ejecutar en el **CPUEmulator** o en el **Web IDE** del curso.

El ejercicio de ejemplo incluido (**NestedSum**) demuestra el funcionamiento completo: traduce y ejecuta un programa que calcula la sumatoria


$S = \sum_{i=0}^{n} \bigl(i^2 + 1\bigr)$


donde `n` es una constante definida en `Sys.vm`.

---

## Características implementadas
- Comandos aritméticos y lógicos: `add`, `sub`, `eq`, `gt`, `lt`, `and`, `or`, `not`, `neg`.  
- Acceso a memoria (`push` / `pop`) para los segmentos: `local`, `argument`, `this`, `that`, `temp`, `pointer`, `static`.  
- Control de flujo: `label`, `goto`, `if-goto`.  
- Manejo de funciones y llamadas: `function`, `call`, `return`.  
- Código de inicialización (bootstrap): configura `SP = 256` y llama automáticamente a `Sys.init` cuando se traduce una carpeta.  
- Traducción de múltiples archivos `.vm` manteniendo el flujo correcto de llamadas entre funciones y evitando conflictos de identificadores `static`.

---

## Estructura del proyecto (ejemplo `NestedSum`)
```
NestedSum/
│
├── VMTranslator.py      # Programa principal (entrada, limpieza y flujo general)
├── Parser.py            # Lee líneas VM, identifica tipo de comando y argumentos
├── CodeWriter.py        # Genera el código Assembly correspondiente
│
├── Main.vm              # Funciones: computeSum, square, addOne
├── Sys.vm               # Punto de entrada: define n y llama a computeSum
│
└── NestedSum.asm        # Salida traducida, lista para ejecutar en CPUEmulator/Web IDE
```

---

## Descripción del programa VM (`NestedSum`)

### `Sys.vm`
Punto de entrada del sistema: define el valor de `n`, llama a `Main.computeSum`, almacena el resultado en `temp 0` (RAM[5]) y entra en un bucle infinito.

```vm
function Sys.init 0
push constant 7        // n = 7
call Main.computeSum 1 // llama a la función principal con un argumento
pop temp 0             // guarda el resultado en RAM[5]
label Sys$END
goto Sys$END
```

---

### `Main.vm`
Contiene las tres funciones principales:

- `Main.computeSum(n)`: ejecuta el ciclo que suma `(i^2 + 1)` para `i = 0..n`.
- `Main.square(x)`: calcula `x * x` por sumas sucesivas.
- `Main.addOne(x)`: retorna `x + 1`.

```vm
// Main.vm

// Suma total = sum_{i=0..n} ( i^2 + 1 )
// Argumento: n está en argument 0
function Main.computeSum 2
push constant 0
pop local 0           // sum = 0
push constant 0
pop local 1           // i = 0

label Main$LOOP
push local 1
push argument 0
gt
if-goto Main$END      // if (i > n) goto END

push local 1
call Main.square 1    // stack: [..., i^2]
call Main.addOne 1    // stack: [..., i^2 + 1]

push local 0
add
pop local 0           // sum += (i^2 + 1)

push local 1
push constant 1
add
pop local 1           // i = i + 1

goto Main$LOOP
label Main$END
push local 0
return

// square(x) = x*x por sumas sucesivas
// locals: res, cnt
function Main.square 2
push constant 0
pop local 0           // res = 0
push argument 0
pop local 1           // cnt = x

label Main$sq_loop
push local 1
push constant 0
gt
if-goto Main$sq_body
goto Main$sq_end

label Main$sq_body
push local 0
push argument 0
add
pop local 0           // res += x
push local 1
push constant 1
sub
pop local 1           // cnt--
goto Main$sq_loop

label Main$sq_end
push local 0
return

// addOne(x) = x + 1
function Main.addOne 0
push argument 0
push constant 1
add
return
```

---

## Uso / Ejecución del traductor

### Traducir una carpeta completa
Desde la línea de comandos:
```bash
python VMTranslator.py path/NestedSum
```
Esto genera:
```
NestedSum/NestedSum.asm
```

El traductor detecta si la entrada es un archivo o una carpeta, limpia los comentarios, aplica el bootstrap (cuando corresponde) y traduce cada módulo `.vm` contenido.

### Ejecutar el programa traducido
1. Abrir `NestedSum.asm` en el **CPUEmulator** del software Nand2Tetris o en el **Web IDE**:
   - https://nand2tetris.github.io/web-ide/chip/
2. Cargar el archivo y ejecutar hasta el final o hasta alcanzar el bucle `Sys$END`.
3. Verificar la memoria RAM en la posición `5` (corresponde a `temp 0`).

---

## Resultado esperado (ejemplo para `n = 7`)
Al observar `RAM[5]` en el CPUEmulator / Web IDE:

```
RAM[5] = 148
```

Esta es la sumatoria \(\sum_{i=0}^{7} (i^2 + 1)\).

Resultados esperados para varios valores de `n`:

```
n  ->  sum_{i=0}^n (i^2 + 1)
0  ->  1
1  ->  3
2  ->  8
3  ->  18
4  ->  35
5  ->  61
6  ->  98
7  ->  148
```

---

## Ejecución paso a paso (resumen)
1. **Bootstrap**: `SP = 256`, se llama a `Sys.init` (si se traduce una carpeta).  
2. **Sys.init**: empuja `n` al stack y realiza `call Main.computeSum`.  
3. **Main.computeSum**: inicializa `sum` e `i`, itera `i = 0..n`:
   - calcula `i^2` llamando a `Main.square`,
   - llama a `Main.addOne` para obtener `i^2 + 1`,
   - acumula en `sum`,
   - incrementa `i`.
4. Al terminar el loop (cuando `i > n`) `computeSum` devuelve `sum`.
5. **Sys.init** guarda el valor en `temp 0` (RAM[5]) y entra en `Sys$END`.

---

## Notas finales
- El traductor soporta correctamente la semántica de llamadas y retornos, manipulación de la pila y segmentos de memoria exigidos por los proyectos 7 y 8 del curso.  
- El proyecto es modular: `Parser.py` y `CodeWriter.py` pueden adaptarse para extender soporte o mejorar generación de código (optimización de etiquetas, manejo de nombres `static` más robusto, etc.).  
- Para probar con distintos `n`, editar `Sys.vm` (el `push constant <n>`) y volver a ejecutar el traductor.

---
