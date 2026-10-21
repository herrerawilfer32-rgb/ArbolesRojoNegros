"""Árbol cromático interno; NIL explícitos, distintos y con peso positivo.

Las inserciones admiten rojo-rojo pendiente. La eliminación exige mantenimiento
previo: simplifica el dominio de las reglas locales de eliminación clásicas.
Cada paso conserva la suma de pesos hasta NIL; normalizar la raíz cambia todas
las sumas por igual. Esta clase requiere sincronización externa.
"""
from dataclasses import dataclass, field
from itertools import count

_ids = count()


@dataclass(eq=False)
class Node:
    key: object = None
    weight: int = 1
    parent: object = None
    left: object = None
    right: object = None
    uid: int = field(default_factory=lambda: next(_ids))

    @property
    def nil(self):
        return self.key is None


class Tree:
    def __init__(self):
        self.root = Node()

    def nodes(self):
        stack = [self.root]
        while stack:
            n = stack.pop()
            yield n
            if not n.nil:
                stack.extend([n.right, n.left])

    def pending(self):
        result = []
        for n in self.nodes():
            if n.weight > 1:
                result.extend(('peso', n.uid, i) for i in range(n.weight - 1))
            if n.parent and n.weight == n.parent.weight == 0:
                result.append(('rojo', n.parent.uid, n.uid))
        return tuple(result)

    def find(self, key):
        n = self.root
        while not n.nil and n.key != key:
            n = n.left if key < n.key else n.right
        return n

    def replace(self, a, b):
        p = a.parent
        b.parent = p
        if p is None:
            self.root = b
        elif p.left is a:
            p.left = b
        else:
            p.right = b

    def rotate(self, x, left):
        y = x.right if left else x.left
        assert not y.nil
        self.replace(x, y)
        if left:
            x.right = y.left
            x.right.parent = x
            y.left = x
        else:
            x.left = y.right
            x.left.parent = x
            y.right = x
        x.parent = y

    def insert(self, key):
        if any(n.weight > 1 for n in self.nodes()):
            raise ValueError('La inserción requiere resolver primero el exceso de peso')
        n = self.find(key)
        if not n.nil:
            return f'Duplicado rechazado: {key}'
        n.key, n.weight = key, 0
        n.left, n.right = Node(parent=n), Node(parent=n)
        if n is self.root:
            n.weight = 1
        return f'Insertado {key}'

    def delete(self, key):
        if self.pending():
            raise ValueError('La eliminación requiere mantenimiento previo')
        n = self.find(key)
        if n.nil:
            return f'Valor inexistente: {key}'
        if not n.left.nil and not n.right.nil:
            s = n.right
            while not s.left.nil:
                s = s.left
            n.key = s.key
            n = s
        child = n.right if n.left.nil else n.left
        child.weight += n.weight
        self.replace(n, child)
        return f'Eliminado {key}; peso transferido al sustituto: {child.weight}'

    def step(self):
        # La raíz roja es una normalización adicional, no una arista roja-roja.
        if self.root.weight != 1:
            uid = self.root.uid
            self.root.weight = 1
            return uid, 'Normalización del peso de la raíz a 1'
        # Preorden: el primer conflicto tiene abuelo de peso positivo.
        for x in self.nodes():
            p = x.parent
            if p is None or x.weight != 0 or p.weight != 0:
                continue
            g = p.parent
            assert g is not None and g.weight > 0
            left = p is g.left
            u = g.right if left else g.left
            if u.weight == 0:
                p.weight = u.weight = 1
                g.weight -= 1
                return g.uid, 'Rojo-rojo: padres +1 y abuelo −1'
            if x is (p.right if left else p.left):
                self.rotate(p, left)
                p = x
            old = g.weight
            self.rotate(g, not left)
            p.weight, g.weight = old, 0
            return p.uid, 'Rojo-rojo: rotación simple/doble y transferencia de pesos'
        for x in self.nodes():
            if x.weight <= 1:
                continue
            p = x.parent
            left = x is p.left
            s = p.right if left else p.left
            assert not s.nil
            if s.weight == 0:
                self.rotate(p, left)
                s.weight, p.weight = p.weight, 0
                return p.uid, 'Exceso: rotación de hermano rojo y cambio de pesos'
            near, far = (s.left, s.right) if left else (s.right, s.left)
            if near.weight > 0 and far.weight > 0:
                x.weight -= 1
                s.weight -= 1
                p.weight += 1
                return p.uid, 'Exceso: hijos −1, padre +1 (propagación)'
            if far.weight > 0:
                self.rotate(s, not left)
                near.weight, s.weight = s.weight, 0
                return near.uid, 'Exceso: rotación del sobrino cercano y cambio de pesos'
            self.rotate(p, left)
            s.weight, p.weight = p.weight, 1
            far.weight += 1
            x.weight -= 1
            return s.uid, 'Exceso: rotación final y redistribución de pesos'
        return None, 'Sin pendientes'

    def validate(self):
        seen = set()
        def visit(n, parent, lo, hi):
            assert n.uid not in seen, 'Ciclo o nodo compartido'
            seen.add(n.uid)
            assert n.parent is parent
            assert isinstance(n.weight, int) and n.weight >= 0
            if n.nil:
                assert n.weight >= 1 and n.left is None and n.right is None
                return n.weight
            assert (lo is None or lo < n.key) and (hi is None or n.key < hi)
            a = visit(n.left, n, lo, n.key)
            b = visit(n.right, n, n.key, hi)
            assert a == b, f'Sumas desiguales en {n.key}: {a}, {b}'
            return a + n.weight
        return visit(self.root, None, None, None)

    def snapshot(self):
        return tuple((n.uid, n.key, n.weight,
                      n.parent.uid if n.parent else None)
                     for n in self.nodes())
