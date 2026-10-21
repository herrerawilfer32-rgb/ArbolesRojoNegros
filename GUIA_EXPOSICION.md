# Guía de exposición del programa — 3 a 4 minutos

Duración objetivo: **3 minutos y 40 segundos**, incluyendo una demostración.
Antes de empezar, abre el programa con n=10, modo aviso y pausa de 1 segundo.
Deja abiertos `chromatic.py` y `app.py`. Ensaya con cronómetro; los tiempos
incluyen cambiar entre el editor y la ventana.

**Cómo ubicarte:** «pestaña» significa el archivo abierto en el editor.
En VS Code puedes pulsar **Ctrl+P**, escribir el nombre del archivo y abrirlo;
después usa **Ctrl+G** para ir a la línea indicada. Las ubicaciones siguientes
son ayudas para navegar, no texto adicional para leer durante la exposición.

## 1. Objetivo y diferencia — 0:00 a 0:35

**Pestaña a mostrar:** `chromatic.py`, línea **1**, comentario inicial que
describe la variante y sus restricciones. Para estudiar la comparación,
consulta la sección «Variante y reglas» de `README.md`.

«Este programa visualiza un árbol rojo-negro relajado, usando una variante
cromática. En un rojo-negro clásico, cada operación restaura las reglas antes
de terminar. Aquí, algunas modificaciones pueden dejar conflictos pendientes
que otro trabajador repara después. Siempre se conserva el orden de búsqueda:
menores a la izquierda y mayores a la derecha».

## 2. Representación y contador — 0:35 a 1:15

**Pestaña a mostrar:** `chromatic.py`. Ve a **15** para `Node` (clave, peso y
enlaces), a **24** para la propiedad `nil` y a **40** para `pending()`
(contador). Basta señalar `Node` y `pending()` durante la exposición.

«Cada nodo almacena una clave, enlaces y un peso. Cero representa rojo; uno,
negro; y un valor mayor que uno, exceso de negro. NIL representa un enlace
vacío y también tiene peso. Se mantiene igual la suma de pesos de los caminos
hasta NIL. El contador suma una infracción por cada arista rojo-rojo y una por
cada unidad de exceso. Por ejemplo, un nodo de peso tres aporta dos».

## 3. Operaciones y reparación — 1:15 a 1:55

**Pestaña a mostrar:** `chromatic.py`. Señala `insert()` en la línea **79**,
`delete()` en la **91** y `step()` en la **108**, sin leer sus líneas completas.
Si preguntan por el cambio de enlaces, `rotate()` empieza en la línea **65**.

«Insertar convierte un NIL en un nodo rojo con dos NIL: el peso del camino
sigue siendo uno, porque cero más uno es uno. Al eliminar se transfiere el peso
al sustituto, lo que puede producir exceso. La función step realiza una
reparación local con cambios de peso y, cuando corresponde, rotaciones.
No reconstruye todo el árbol. Esta variante exige reparar antes de eliminar
y antes de insertar cuando existe exceso de peso».

## 4. Demostración — 1:55 a 2:45

**Ventana a mostrar:** la aplicación «Árbol cromático», fuera del editor.
Se abre haciendo doble clic en `ejecutar.bat` desde el explorador de archivos;
abrir su pestaña en el editor solo muestra el lanzador, no ejecuta el programa.
Los controles están definidos en `app.py`, clase `App`, línea **131**, y el
dibujo en `draw()`, línea **229**. Durante esta parte muestra la ventana,
sin cambiar al código.

1. Inserta **10, 5, 1**. Señala la arista roja entre 5 y 1.
2. Inserta **20**. Explica: «Otra inserción terminó con el conflicto pendiente».
3. Pulsa **Mantenimiento**. Señala el registro y espera al contador cero.
4. Explica: «Primero se solicita mantenimiento y después se ejecuta. En este
   ejemplo se resuelve mediante cambios de peso; no toda reparación rota».

## 5. Hilos, políticas y validación — 2:45 a 3:40

**Pestañas a mostrar:** primero `app.py`, clase `Engine`, línea **9**;
después `chromatic.py`, función `validate()`, línea **162**.

Para estudiar los detalles de `app.py`: `Engine.__init__()` (línea **10**)
crea el bloqueo, las colas y los trabajadores; `modify()` (**64**) procesa
operaciones; `repair()` (**90**) hace mantenimiento; `configure()` (**48**)
y `wait_for()` (**56**) coordinan el límite y la espera. `publish()` (**31**)
publica instantáneas y `App.poll()` (**214**) recibe los eventos para dibujar.
No recorras todos estos métodos en la exposición: muestra solo `Engine`
y `validate()` para respetar el tiempo.

**Respaldo de las pruebas, solo si preguntan:** pestaña `test_app.py`, línea
**45**, prueba aleatoria; línea **72**, pruebas de trabajadores. La pestaña
`smoke_gui.py` contiene la prueba de la ventana y `VALIDACION.md` registra
los resultados ejecutados.

«El hilo principal atiende Tkinter; un trabajador modifica y otro repara.
Un bloqueo evita cambios simultáneos en los enlaces, y las colas transportan
tareas e instantáneas para dibujar. En modo aviso, superar n solicita
mantenimiento. En modo estricto, una operación que supera n queda provisional
hasta cumplir el límite, sin congelar la ventana. Estas políticas son propias
de la aplicación.

La función validate comprueba orden, enlaces y sumas de pesos. Pasaron seis
pruebas, incluidas 10.500 modificaciones aleatorias, y una prueba gráfica.
El objetivo es observar el mantenimiento diferido; no se ha demostrado que
esta implementación sea más rápida que un rojo-negro clásico».

## Repaso de estudio — fuera del tiempo de exposición

| Elemento | Pestaña y línea inicial | Idea que debes recordar |
|---|---|---|
| `Node` | `chromatic.py`: 15 | Peso 0 rojo, 1 negro, mayor que 1 exceso; NIL no es el número cero. |
| `pending()` | `chromatic.py`: 40 | Cuenta aristas rojo-rojo y unidades de exceso, incluidos NIL. |
| `insert()` | `chromatic.py`: 79 | Sustituye NIL de peso 1 por rojo y dos NIL: 1 = 0 + 1. |
| `delete()` | `chromatic.py`: 91 | Usa sucesor si hay dos hijos y transfiere peso al sustituto. |
| `step()` / `rotate()` | `chromatic.py`: 108 / 65 | Repara localmente conservando el orden y las sumas. |
| `validate()` | `chromatic.py`: 162 | Revisa las propiedades estructurales y los pesos de caminos. |
| `Engine` | `app.py`: 9 | Coordina trabajadores mediante cola, condición y bloqueo. |
| `publish()` / `poll()` | `app.py`: 31 / 214 | Publica una instantánea consistente y la dibuja en Tkinter. |
| Controles / `draw()` | `app.py`: 131 / 229 | Construye la interfaz y dibuja nodos, aristas y marcas. |
| Pruebas del modelo / trabajadores | `test_app.py`: 17 / 72 | Comprueba invariantes y coordinación de las políticas. |
| Lanzador | `ejecutar.bat`: 1 | Busca el intérprete y ejecuta `app.py`. |

**Ruta rápida de pestañas durante la exposición:** `chromatic.py` (partes
1–3) → ventana del programa (parte 4) → `app.py` → `chromatic.py`
(parte 5). Las líneas corresponden a la versión actual; si cambian al editar,
busca el nombre de la clase o función con **Ctrl+F**.

## Respuestas rápidas — solo si preguntan

- **¿Relajado significa desordenado?** No: conserva el orden BST y las sumas de
  pesos; admite temporalmente los conflictos definidos.
- **¿El peso es un factor AVL?** No: representa contribución de peso negro.
- **¿n cuenta nodos?** No: cuenta infracciones. Peso 3 aporta dos infracciones.
- **¿El clásico tiene doble negro?** Puede usarlo durante la eliminación;
  aquí el exceso queda explícito y su reparación puede diferirse.
- **¿Todas las operaciones continúan con conflictos?** No: esta variante
  restringe eliminaciones e inserciones con exceso de peso.
- **¿Contador cero significa raíz negra?** No necesariamente; el mantenimiento
  completo también normaliza la raíz a peso 1.
- **¿Dos hilos modifican a la vez?** No dentro del bloqueo: se alternan.
- **¿Todo es O(log N)?** No se garantiza para este programa: cuenta, valida y
  publica mediante recorridos completos, y los conflictos pueden aumentar altura.

Para mantenerte por debajo de cuatro minutos, realiza una sola demostración
y explica verbalmente el modo estricto. Las respuestas anteriores son material
de estudio, no parte del guion cronometrado.
