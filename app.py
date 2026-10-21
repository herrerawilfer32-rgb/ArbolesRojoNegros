"""Ejecutar con Python 3.10 o posterior: python app.py."""
import queue
import threading
import tkinter as tk
from tkinter import ttk
from chromatic import Tree


class Engine:
    def __init__(self):
        self.tree = Tree()
        self.cv = threading.Condition(threading.RLock())
        self.commands = queue.Queue()
        self.events = queue.Queue()
        self.stop = threading.Event()
        self.requested = False
        self.limit = 3
        self.strict = False
        self.delay = 0.7
        self.worker = 'Disponible'
        self.maintenance = 'En reposo'
        self.current = None
        self.pending = ()
        self.threads = [threading.Thread(target=self.modify, name='Modificaciones'),
                        threading.Thread(target=self.repair, name='Mantenimiento')]
        for thread in self.threads:
            thread.start()
        with self.cv:
            self.publish('Aplicación lista')

    def publish(self, message=''):
        self.tree.validate()
        self.pending = self.tree.pending()  # sustituye, nunca acumula referencias
        self.events.put((self.tree.snapshot(), self.pending, self.current,
                         self.worker, self.maintenance, message))

    def request_locked(self):
        self.requested = True
        if self.maintenance != 'Reparando':
            self.maintenance = 'Solicitado (aún no ejecutado)'
        self.cv.notify_all()

    def request(self):
        with self.cv:
            self.request_locked()
            self.publish('Mantenimiento completo solicitado')

    def configure(self, limit, strict, delay):
        with self.cv:
            self.limit, self.strict, self.delay = limit, strict, delay
            if len(self.pending) > limit:
                self.request_locked()
            self.publish('Configuración aplicada')
            self.cv.notify_all()

    def wait_for(self, predicate):
        while predicate() and not self.stop.is_set():
            self.worker = 'Esperando mantenimiento'
            self.request_locked()
            self.publish()
            self.cv.wait()
        return not self.stop.is_set()

    def modify(self):
        try:
            while not self.stop.is_set():
                item = self.commands.get()
                if item is None:
                    return
                operation, key = item
                with self.cv:
                    def blocked():
                        return ((self.strict and len(self.pending) > self.limit)
                                or (operation == 'delete' and bool(self.pending))
                                or any(n.weight > 1 for n in self.tree.nodes()))
                    if not self.wait_for(blocked):
                        return
                    self.worker = f'Ejecutando {operation} {key}'
                    result = getattr(self.tree, operation)(key)
                    self.publish(result + ' (provisional)')
                    if len(self.pending) > self.limit:
                        self.request_locked()
                    if not self.wait_for(lambda: self.strict and len(self.pending) > self.limit):
                        return
                    self.worker = 'Disponible'
                    self.publish(result + ' — operación confirmada')
        except Exception as exc:
            self.fail(exc)

    def repair(self):
        try:
            while not self.stop.is_set():
                with self.cv:
                    self.cv.wait_for(lambda: self.requested or self.stop.is_set())
                    if self.stop.is_set():
                        return
                    delay = self.delay
                # La solicitud no equivale a ejecución; la pausa no retiene el bloqueo.
                if self.stop.wait(delay):
                    return
                with self.cv:
                    if not self.pending and self.tree.root.weight == 1:
                        self.requested = False
                        self.current = None
                        self.maintenance = 'En reposo'
                        self.publish('Mantenimiento completo terminado')
                    else:
                        self.maintenance = 'Reparando'
                        self.current, message = self.tree.step()
                        self.publish(message)
                    self.cv.notify_all()
        except Exception as exc:
            self.fail(exc)

    def fail(self, exc):
        with self.cv:
            self.worker = self.maintenance = f'ERROR: {exc!r}'
            self.events.put((self.tree.snapshot(), self.tree.pending(), None,
                             self.worker, self.maintenance, self.worker))
            self.stop.set()
            self.commands.put(None)
            self.cv.notify_all()

    def close(self):
        self.stop.set()
        self.commands.put(None)
        with self.cv:
            self.cv.notify_all()


class App:
    def __init__(self, root):
        self.root = root
        root.title('Árbol cromático · laboratorio de mantenimiento diferido')
        root.geometry('1180x820')
        self.engine = Engine()
        self.closing = False
        bar = ttk.Frame(root, padding=10)
        bar.pack(fill='x')
        ttk.Label(bar, text='Entero:').pack(side='left')
        self.value = ttk.Entry(bar, width=12)
        self.value.pack(side='left', padx=5)
        for title, op in [('Insertar', 'insert'), ('Eliminar', 'delete')]:
            ttk.Button(bar, text=title, command=lambda o=op: self.submit(o)).pack(side='left', padx=3)
        ttk.Button(bar, text='Mantenimiento', command=self.engine.request).pack(side='left', padx=8)
        ttk.Label(bar, text='Máximo n:').pack(side='left')
        self.limit = tk.StringVar(value='3')
        ttk.Entry(bar, textvariable=self.limit, width=6).pack(side='left', padx=5)
        self.policy = tk.StringVar(value='Límite como aviso')
        ttk.Combobox(bar, textvariable=self.policy, state='readonly', width=21,
                     values=['Límite como aviso', 'Límite estricto']).pack(side='left')
        ttk.Button(bar, text='Aplicar', command=self.configure).pack(side='left', padx=5)
        speed = ttk.Frame(root, padding=(10, 0))
        speed.pack(fill='x')
        ttk.Label(speed, text='Pausa entre reparaciones (0,05–2 segundos):').pack(side='left')
        self.delay = tk.DoubleVar(value=0.7)
        ttk.Scale(speed, from_=0.05, to=2, variable=self.delay,
                  command=lambda _: self.speed()).pack(side='left', fill='x', expand=True)
        self.status = tk.StringVar()
        ttk.Label(root, textvariable=self.status, padding=10).pack(fill='x')
        ttk.Label(root, text='Rojo: peso 0 · Negro: peso 1 · Naranja: exceso (incluye NIL) · '
                  'Magenta: conflicto rojo-rojo · Azul: nodo de la última reparación',
                  padding=(10, 0)).pack(fill='x')
        frame = ttk.Frame(root)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.canvas = tk.Canvas(frame, background='#f1f5f9')
        sx = ttk.Scrollbar(frame, orient='horizontal', command=self.canvas.xview)
        sy = ttk.Scrollbar(frame, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=sx.set, yscrollcommand=sy.set)
        self.canvas.grid(row=0, column=0, sticky='nsew')
        sy.grid(row=0, column=1, sticky='ns')
        sx.grid(row=1, column=0, sticky='ew')
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        self.log = tk.Text(root, height=8, state='disabled', wrap='word')
        self.log.pack(fill='x', padx=10, pady=(0, 10))
        self.value.bind('<Return>', lambda _: self.submit('insert'))
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(40, self.poll)

    def note(self, text):
        self.log.configure(state='normal')
        self.log.insert('end', text + '\n')
        if int(self.log.index('end-1c').split('.')[0]) > 150:
            self.log.delete('1.0', '2.0')
        self.log.see('end')
        self.log.configure(state='disabled')

    def speed(self):
        with self.engine.cv:
            self.engine.delay = self.delay.get()

    def configure(self):
        try:
            limit = int(self.limit.get())
            if limit < 0:
                raise ValueError
        except ValueError:
            self.note('n debe ser un entero mayor o igual que 0.')
            return False
        self.engine.configure(limit, self.policy.get() == 'Límite estricto', self.delay.get())
        return True

    def submit(self, op):
        try:
            key = int(self.value.get())
        except ValueError:
            self.note('Introduce un número entero válido.')
            return
        if self.configure():
            self.engine.commands.put((op, key))
            self.note(f'En cola: {op} {key}')

    def poll(self):
        if self.closing:
            return
        # Un evento por cuadro conserva los estados intermedios publicados.
        try:
            nodes, pending, current, worker, maintenance, message = self.engine.events.get_nowait()
            self.status.set(f'Infracciones: {len(pending)}  |  Modificaciones: {worker}\n'
                            f'Mantenimiento: {maintenance}')
            if message:
                self.note(message + f' · pendientes: {len(pending)}')
            self.draw(nodes, pending, current)
        except queue.Empty:
            pass
        self.root.after(40, self.poll)

    def draw(self, nodes, pending, current):
        self.canvas.delete('all')
        data = {n[0]: n for n in nodes}
        children = {n[0]: [] for n in nodes}
        for uid, key, weight, parent in nodes:
            if parent is not None:
                children[parent].append(uid)
        # Inorden iterativo: una columna exclusiva por nodo, incluidos NIL.
        positions, order = {}, []
        stack = [(nodes[0][0], 0, False)]
        while stack:
            uid, depth, visited = stack.pop()
            cs = children[uid]
            if visited or not cs:
                order.append((uid, depth))
            else:
                stack.extend([(cs[1], depth + 1, False), (uid, depth, True),
                              (cs[0], depth + 1, False)])
        width = max(84, max(len(str(n[1])) for n in nodes) * 9 + 24)
        for index, (uid, depth) in enumerate(order):
            positions[uid] = (55 + index * width, 50 + depth * 95)
        rr = {(p[1], p[2]) for p in pending if p[0] == 'rojo'}
        conflicted = {u for edge in rr for u in edge}
        for uid, key, weight, parent in nodes:
            x, y = positions[uid]
            if parent is not None:
                px, py = positions[parent]
                self.canvas.create_line(px, py, x, y, width=3,
                                        fill='#c026d3' if (parent, uid) in rr else '#94a3b8')
        for uid, key, weight, parent in nodes:
            x, y = positions[uid]
            radius = 19 if key is None else max(25, len(str(key)) * 4.5 + 9)
            color = '#dc2626' if weight == 0 else '#172033'
            outline = '#f97316' if weight > 1 else '#c026d3' if uid in conflicted else color
            if uid == current:
                self.canvas.create_oval(x-radius-6, y-32, x+radius+6, y+32,
                                        outline='#0284c7', width=3)
            self.canvas.create_oval(x-radius, y-25, x+radius, y+25,
                                    fill=color, outline=outline, width=4)
            self.canvas.create_text(x, y, text='NIL' if key is None else str(key), fill='white')
            self.canvas.create_text(x, y+39, text=f'{"⚠ " if weight > 1 else ""}peso {weight}',
                                    fill='#c2410c' if weight > 1 else '#475569')
        bbox = self.canvas.bbox('all')
        self.canvas.configure(scrollregion=(0, 0, bbox[2]+40, bbox[3]+40))

    def close(self):
        self.closing = True
        self.engine.close()
        self.finish_close()

    def finish_close(self):
        if any(t.is_alive() for t in self.engine.threads):
            self.root.after(20, self.finish_close)
        else:
            self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    App(root)
    root.mainloop()
