from unittest import TestCase
import poker


class TestPoker(TestCase):
    def test_flush(self):
        self.assertEqual(poker.flush("6C 7C 8C 9C TC".split()), True)
        self.assertEqual(poker.flush("6C 7S 8C 9C TC".split()), False)

    def test_street(self):
        self.assertEqual(poker.straight([6, 5, 4, 3, 2]), True)
        self.assertEqual(poker.straight([14, 6, 5, 4, 3]), False)
        self.assertEqual(poker.straight([5, 4, 3, 2, 14]), True)
        self.assertEqual(poker.straight([14, 13, 12, 11, 10]), True)

    def test_kind(self):
        self.assertEqual(poker.kind(1, [10, 6, 5, 4, 3]), 10)
        self.assertEqual(poker.kind(2, [14, 14, 14, 10, 10]), 10)
        self.assertEqual(poker.kind(3, [10, 10, 14, 14, 14]), 14)
