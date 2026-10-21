# Guía de exposición del programa — 3 a 4 minutos

Duración objetivo: **3 minutos y 40 segundos**, incluyendo una demostración.
Antes de empezar, abre el programa con n=10, modo aviso y pausa de 1 segundo.
Deja abiertos `chromatic.py` y `app.py`. Ensaya con cronómetro; los tiempos
incluyen cambiar entre el editor y la ventana.

## 1. Objetivo y diferencia — 0:00 a 0:35

«Este programa visualiza un árbol rojo-negro relajado, usando una variante
cromática. En un rojo-negro clásico, cada operación restaura las reglas antes
de terminar. Aquí, algunas modificaciones pueden dejar conflictos pendientes
que otro trabajador repara después. Siempre se conserva el orden de búsqueda:
menores a la izquierda y mayores a la derecha».

## 2. Representación y contador — 0:35 a 1:15

Muestra `Node` y `pending()` en `chromatic.py`.

«Cada nodo almacena una clave, enlaces y un peso. Cero representa rojo; uno,
negro; y un valor mayor que uno, exceso de negro. NIL representa un enlace
vacío y también tiene peso. Se mantiene igual la suma de pesos de los caminos
hasta NIL. El contador suma una infracción por cada arista rojo-rojo y una por
cada unidad de exceso. Por ejemplo, un nodo de peso tres aporta dos».

## 3. Operaciones y reparación — 1:15 a 1:55

Señala `insert()`, `delete()` y `step()` sin leer sus líneas completas.

«Insertar convierte un NIL en un nodo rojo con dos NIL: el peso del camino
sigue siendo uno, porque cero más uno es uno. Al eliminar se transfiere el peso
al sustituto, lo que puede producir exceso. La función step realiza una
reparación local con cambios de peso y, cuando corresponde, rotaciones.
No reconstruye todo el árbol. Esta variante exige reparar antes de eliminar
y antes de insertar cuando existe exceso de peso».

## 4. Demostración — 1:55 a 2:45

1. Inserta **10, 5, 1**. Señala la arista roja entre 5 y 1.
2. Inserta **20**. Explica: «Otra inserción terminó con el conflicto pendiente».
3. Pulsa **Mantenimiento**. Señala el registro y espera al contador cero.
4. Explica: «Primero se solicita mantenimiento y después se ejecuta. En este
   ejemplo se resuelve mediante cambios de peso; no toda reparación rota».

## 5. Hilos, políticas y validación — 2:45 a 3:40

Muestra brevemente `Engine` en `app.py` y termina señalando `validate()`.

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

| Elemento | Idea que debes recordar |
|---|---|
| `Node` | Peso 0 rojo, 1 negro, mayor que 1 exceso; NIL no es el número cero. |
| `pending()` | Cuenta aristas rojo-rojo y unidades de exceso, incluidos NIL. |
| `insert()` | Sustituye NIL de peso 1 por rojo y dos NIL: 1 = 0 + 1. |
| `delete()` | Usa sucesor si hay dos hijos y transfiere peso al sustituto. |
| `step()` / `rotate()` | Repara localmente conservando el orden y las sumas. |
| `validate()` | Revisa las propiedades estructurales y los pesos de caminos. |
| `Engine` | Coordina trabajadores mediante cola, condición y bloqueo. |
| `publish()` / `poll()` | Publica una instantánea consistente y la dibuja en Tkinter. |

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
