# Comprobaciones ejecutadas

Fecha: 21 de octubre de 2026.

- `python -m unittest -v test_app`: 6 pruebas correctas, 4,486 segundos.
- La prueba aleatoria ejecuta 10.500 modificaciones, además de reparaciones y
  vaciado final de cada árbol; valida invariantes después de cada paso.
- `python smoke_gui.py`: `GUI OK: ventana, operaciones, Canvas y cierre`.

Se utilizó el intérprete local indicado en README.md. La prueba gráfica falló
inicialmente al cargar Tcl dentro del aislamiento de herramientas. Al ejecutar
la misma prueba fuera de ese aislamiento, pasó sin cambios en el programa.

No se realizó una auditoría visual exhaustiva ni una demostración formal de
terminación para todas las secuencias posibles. Las restricciones de esta
variante y sus límites prácticos están documentados en README.md.
