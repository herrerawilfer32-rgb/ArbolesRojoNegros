"""Prueba real de Tkinter: ventana, callbacks, dibujo y cierre de trabajadores."""
import time
import tkinter as tk
from app import App

root = tk.Tk()
app = App(root)
app.limit.set('0')
app.policy.set('Límite estricto')
app.delay.set(.05)
for key in [10, 5, 1, 20]:
    app.value.delete(0, 'end')
    app.value.insert(0, str(key))
    app.submit('insert')
deadline = time.monotonic() + 3
while time.monotonic() < deadline:
    root.update()
    time.sleep(.01)
assert app.canvas.find_all(), 'Canvas sin elementos'
with app.engine.cv:
    app.engine.tree.validate()
    assert not app.engine.pending
    assert not app.engine.tree.find(20).nil
app.close()
while any(t.is_alive() for t in app.engine.threads):
    root.update()
    time.sleep(.01)
try:
    root.update()
except tk.TclError:
    pass
print('GUI OK: ventana, operaciones, Canvas y cierre')
