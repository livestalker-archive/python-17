from unittest import TestCase
import deco


def foo(x1, x2):
    return x1 + x2


class TestDeco(TestCase):
    def test_n_ary(self):
        n_ary = deco.n_ary(foo)
        self.assertEqual(n_ary(1, 2, 3, 4, 5), sum(range(1, 6)))

    def test_countcalls(self):
        counted = deco.countcalls(foo)
        counted(1, 2)
        counted(1, 2)
        counted(1, 2)
        self.assertEqual(counted.calls, 3)

    def test_countcalls_and_n_ary(self):
        mixed = deco.countcalls(deco.n_ary(foo))
        self.assertEqual(mixed(1, 2, 3), 6)
        self.assertEqual(mixed.calls, 1)
        mixed = deco.n_ary(deco.countcalls(foo))
        self.assertEqual(mixed(1, 2, 3), 6)
        self.assertEqual(mixed.calls, 1)

    def test_countcalls_and_memo(self):
        mixed = deco.countcalls(deco.memo(foo))
        self.assertEqual(mixed(1, 2), 3)
        self.assertEqual(mixed.calls, 1)
        self.assertEqual(mixed(1, 2), 3)
        self.assertEqual(mixed.calls, 2)

        mixed = deco.memo(deco.countcalls(foo))
        self.assertEqual(mixed(1, 2), 3)
        self.assertEqual(mixed.calls, 1)
        self.assertEqual(mixed(1, 2), 3)
        self.assertEqual(mixed.calls, 2)
