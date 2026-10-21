import random
import time
import unittest
from chromatic import Tree
from app import Engine


def maintain(t):
    for _ in range(10000):
        t.validate()
        if not t.pending() and t.root.weight == 1:
            return
        t.step()
    raise AssertionError('Mantenimiento no terminó')


class ModelTests(unittest.TestCase):
    def test_pending_and_duplicates(self):
        t = Tree()
        for k in [10, 5, 1, 20]:
            t.insert(k)
            t.validate()
        self.assertTrue(t.pending())
        before = t.snapshot()
        self.assertIn('Duplicado', t.insert(5))
        self.assertEqual(before, t.snapshot())
        maintain(t)
        self.assertFalse(t.pending())

    def test_delete_nil_excess(self):
        t = Tree()
        for k in [10, 5, 15, 1]:
            t.insert(k)
        maintain(t)
        t.delete(15)
        t.validate()
        self.assertTrue(any(n.nil and n.weight == 2 for n in t.nodes()))
        maintain(t)
        for k in [10, 5, 1]:
            t.delete(k)
            maintain(t)
        self.assertTrue(t.root.nil)
        self.assertIn('inexistente', t.delete(123))

    def test_randomized(self):
        for seed in range(30):
            rng = random.Random(seed)
            t, expected = Tree(), set()
            for _ in range(350):
                k = rng.randrange(100)
                if rng.random() < .65:
                    if any(n.weight > 1 for n in t.nodes()):
                        maintain(t)
                    t.insert(k)
                    expected.add(k)
                else:
                    maintain(t)
                    t.delete(k)
                    expected.discard(k)
                t.validate()
                self.assertEqual({n.key for n in t.nodes() if not n.nil}, expected)
                self.assertEqual(len(t.pending()), len(set(t.pending())))
                if rng.random() < .2:
                    maintain(t)
            maintain(t)
            for k in list(expected):
                t.delete(k)
                maintain(t)
            self.assertTrue(t.root.nil)


class ThreadTests(unittest.TestCase):
    def setUp(self):
        self.e = Engine()
        self.e.configure(100, False, .01)

    def tearDown(self):
        self.e.close()
        for t in self.e.threads:
            t.join(2)
            self.assertFalse(t.is_alive())

    def wait_until(self, pred):
        until = time.monotonic() + 4
        while time.monotonic() < until:
            with self.e.cv:
                if pred():
                    return
            time.sleep(.005)
        self.fail('Tiempo de espera agotado')

    def insert_conflict(self):
        for k in [10, 5, 1, 20]:
            self.e.commands.put(('insert', k))
        self.wait_until(lambda: not self.e.tree.find(20).nil)

    def test_manual_and_lower_limit(self):
        self.insert_conflict()
        with self.e.cv:
            self.assertTrue(self.e.pending)
            self.assertFalse(self.e.requested)
        self.e.configure(0, True, .01)
        self.wait_until(lambda: not self.e.pending)
        self.e.request()
        self.wait_until(lambda: not self.e.requested)

    def test_strict_wait_and_auto(self):
        self.e.configure(0, True, .08)
        self.insert_conflict()
        self.wait_until(lambda: not self.e.pending and self.e.worker == 'Disponible')
        events = []
        while not self.e.events.empty():
            events.append(self.e.events.get_nowait())
        self.assertTrue(any(e[3] == 'Esperando mantenimiento' for e in events))
        self.assertTrue(any(e[4].startswith('Solicitado') for e in events))
        for e in events:
            if 'confirmada' in e[5]:
                self.assertEqual(len(e[1]), 0)

    def test_warning_auto(self):
        self.e.configure(0, False, .1)
        self.insert_conflict()
        self.wait_until(lambda: not self.e.pending)
        self.assertFalse(self.e.stop.is_set())


if __name__ == '__main__':
    unittest.main(verbosity=2)
