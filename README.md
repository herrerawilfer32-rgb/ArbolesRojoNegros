# Laboratorio de árbol rojo-negro relajado

Programa Python con Tkinter, sin paquetes de pip. Requiere Python 3.10 o posterior
con Tkinter instalado. En este equipo puede abrirse con doble clic en
`ejecutar.bat`, que utiliza el Python local encontrado y, en otros equipos,
recurre al comando `python`.

Desde una terminal situada en esta carpeta:

```powershell
python app.py
python -m unittest -v test_app
python smoke_gui.py
```

Si el alias `python` de Windows no funciona, el intérprete comprobado aquí es:

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" app.py
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m unittest -v test_app
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" smoke_gui.py
```

## Variante y reglas

Árbol cromático con claves en nodos internos y una hoja NIL distinta por enlace
vacío. Los pesos son enteros: 0 rojo, 1 negro, y >1 exceso de negro. Los NIL
tienen peso >=1 y también pueden acumular exceso. Todos los caminos desde un
nodo hasta NIL, incluyendo ambos extremos, tienen la misma suma de pesos.
El peso no es un factor AVL ni un recuento de nodos de color negro.

La inserción sustituye un NIL de peso 1 por un nodo rojo con dos NIL de peso 1.
La raíz se normaliza a peso 1. Se permiten cadenas rojas pendientes y se
repara primero el conflicto más alto. Un tío rojo permite subir una unidad
de peso; en los otros casos se realizan rotaciones simples o dobles y se
transfiere el peso del abuelo. Cada transformación completa es atómica.

Esta variante restringe la eliminación a estados ya reparados; también exige
resolver excesos antes de insertar. El trabajador solicita y espera ese
mantenimiento sin bloquear Tkinter. Esta restricción está implementada también
como precondición de los métodos del modelo. Otras inserciones pueden continuar
con conflictos rojo-rojo pendientes.

Para eliminar un nodo con dos hijos se copia la clave del sucesor y se elimina
el sucesor. Al retirar el nodo se suma su peso al hijo sustituto, que puede
ser NIL. El exceso se resuelve con las reglas locales de hermano rojo,
propagación hacia el padre, rotación de sobrino cercano y rotación final con
sobrino lejano rojo. La normalización de raíz cambia por igual todas las sumas.
No se reconstruye el árbol durante el mantenimiento.

## Contador y políticas

Se cuenta una infracción por cada arista cuyos extremos tienen peso 0, más
`peso - 1` por cada nodo o NIL con peso >1. La normalización de raíz roja es
una tarea adicional que no cuenta como arista rojo-rojo. Tras cada cambio se
regenera la tupla compartida de pendientes con identificadores únicos de nodos
vivos; no se conservan registros antiguos ni referencias a nodos retirados.

El límite es una política didáctica de esta aplicación, no una regla universal
de árboles cromáticos. El botón **Aplicar** confirma la configuración; insertar
o eliminar también aplica los valores visibles. El control de velocidad cambia
inmediatamente la pausa de las siguientes reparaciones.

- **Aviso:** superar n solicita mantenimiento completo; pueden continuar las
  modificaciones admitidas por las precondiciones anteriores.
- **Estricto:** si el estado provisional excede n, la operación aparece como
  «Esperando mantenimiento» y no se confirma ni se toma la siguiente operación
  hasta satisfacer el límite. El árbol provisional es visible y conserva sus
  invariantes estructurales. No se ofrece aislamiento de lectura transaccional.
- Reducir n por debajo del contador solicita mantenimiento; en modo estricto
  se retienen nuevas modificaciones mientras el contador exceda el nuevo n.
- **Mantenimiento** siempre solicita reparación completa. La solicitud y la
  ejecución se muestran como estados distintos; despertar un hilo no implica
  que ya haya ejecutado la reparación.

## Ejemplos reproducibles

Abra una ventana nueva para cada ejemplo. Escriba cada valor y pulse Insertar.

1. **Pendiente mientras ocurre otra operación:** n=10, aviso, Aplicar. Inserte
   10, 5, 1: queda la arista roja 5–1. Inserte 20: el conflicto sigue pendiente.
   Pulse Mantenimiento para observar su resolución manual.
2. **Activación automática:** n=0, aviso, pausa de 2 segundos. Inserte 10, 5,
   1. Aparecerá la solicitud antes de que comience la reparación; el registro
   conserva la secuencia incluso si la ejecución es rápida.
3. **Espera estricta:** n=0, estricto, pausa de 2 segundos. Inserte 10, 5, 1.
   La tercera inserción queda provisional y muestra Esperando mantenimiento.
   Puede encolar 20: se procesará después de confirmar la anterior.
4. **Exceso en NIL:** n=10, aviso. Inserte 10, 5, 15, 1 y pulse Mantenimiento.
   Espere a que termine. Elimine 15: el NIL sustituto tendrá peso 2, señalado
   en naranja. Pulse Mantenimiento y observe la rotación y los nuevos pesos.
5. **Reducción del límite:** repita el ejemplo 1 sin reparar. Seleccione
   estricto, cambie n a 0 y pulse Aplicar. Se solicita reparación; las nuevas
   modificaciones esperan si aún se excede el límite.

Los NIL se dibujan para mostrar los excesos tras borrar. Cada nodo ocupa una
columna de inorden; use las barras horizontal y vertical en árboles grandes.
El anillo azul indica el nodo de la última transformación de mantenimiento,
y se retira al finalizar el mantenimiento completo.

## Sincronización y validación

El hilo principal solo gestiona Tkinter. Un trabajador consume la cola de
modificaciones y otro realiza mantenimiento. Un `Condition` con `RLock`
protege estructura, configuración, pendientes y creación de instantáneas
inmutables. Las esperas liberan el bloqueo; las pausas son interrumpibles.
Los trabajadores nunca acceden a widgets. Tkinter consume los eventos en orden,
uno por cuadro, por lo que puede existir un retraso visual si se encolan muchas
operaciones. El cierre despierta a ambos trabajadores y espera su salida sin
hacer un `join` bloqueante en el hilo gráfico.

Las pruebas revisan orden BST, enlaces padre/hijo, ausencia de ciclos,
integridad de NIL, sumas de pesos y ausencia de conflictos tras mantenimiento.
Incluyen duplicados, valores inexistentes, vaciado, exceso en NIL, 30 semillas
con 350 modificaciones cada una, mantenimiento intercalado y pruebas de los
trabajadores para las políticas. `smoke_gui.py` abre una ventana real, ejecuta
callbacks, comprueba el dibujo y cierra los hilos.

Es una implementación didáctica, no una estructura optimizada para producción:
recorre el árbol para validar, contar y publicar; la validación es recursiva y
está sujeta al límite de recursión de Python en árboles extremadamente profundos.
Las pruebas aportan evidencia, no una demostración formal de corrección o de
rendimiento asintótico del sistema concurrente.
