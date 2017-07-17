#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts), 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета. Черный джокер '?B' может быть
# использован в качестве треф или пик любого ранга, красный
# джокер '?R' - в качестве черв и бубен люього ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertoolsю
# Можно свободно определять свои функции и т.п.
# -----------------
import itertools
import collections
import copy

SYMBOL_RANKS = '23456789TJQKA'
BLACK_SUITS = 'CS'
RED_SUITS = 'HD'
LETTERS = dict(zip(SYMBOL_RANKS, range(2, 16)))  # map ranks to int
RANKS = '14 13 12 11 10 9 8 7 6 5 4 3 2'
LOWEST_STRAIGHT = '14 5 4 3 2'  # straight can start with A


def hand_rank(hand):
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return (8, max(ranks))
    elif kind(4, ranks):
        return (7, kind(4, ranks), kind(1, ranks))
    elif kind(3, ranks) and kind(2, ranks):
        return (6, kind(3, ranks), kind(2, ranks))
    elif flush(hand):
        return (5, ranks)
    elif straight(ranks):
        return (4, max(ranks))
    elif kind(3, ranks):
        return (3, kind(3, ranks), ranks)
    elif two_pair(ranks):
        return (2, two_pair(ranks), ranks)
    elif kind(2, ranks):
        return (1, kind(2, ranks), ranks)
    else:
        return (0, ranks)


def card_ranks(hand):
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    ranks = sorted([LETTERS.get(el[0]) for el in hand], reverse=True)
    return ranks


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    suit = set(el[1] for el in hand)
    return len(suit) == 1


def straight(ranks):
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)

    Alexey notes: я бы в эту функцию передавал не ранги а hand, получилось бы красивее.
    Т.е. helper_ranks бы поменялась на A 2 3 4 5 6 7 8 9 T J Q K A и так же проверял бы на вхождение
    отсортировонной руки в строке через in.
    """
    inner_seq = ' '.join(str(el) for el in ranks)
    return inner_seq in RANKS or inner_seq in LOWEST_STRAIGHT


def _find_equal_n(n, ranks):
    """Поиск рангов, которые повторяются n раз."""
    counts = collections.Counter(ranks)
    equal_n = [k for k in sorted(counts.keys(), reverse=True) if counts[k] == n]
    return equal_n


def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    equal_n = _find_equal_n(n, ranks)
    if len(equal_n) > 0:
        return equal_n[0]
    else:
        return None


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    equal_n = _find_equal_n(2, ranks)
    return None if len(equal_n) != 2 else equal_n


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    five_cards_hands = list(itertools.combinations(hand, 5))
    result = max(five_cards_hands, key=hand_rank)
    return result


def variants(hand):
    for card in hand:
        if not card.startswith('?'):
            yield [card]
        else:
            color = card[1]
            suits = BLACK_SUITS if color == 'B' else RED_SUITS
            # удаляем из вариантов, которые дают джокеры, карты, которые уже на руках
            # иначе в itertools.product мы получим неправильные руки - руки с двумя одинаковыми картами
            yield set(r + s for r in SYMBOL_RANKS for s in suits) - set(hand)


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    hands = list(itertools.product(*variants(hand)))
    bests = set([best_hand(el) for el in hands])
    return max(bests, key=hand_rank)


def test_best_hand():
    print "test_best_hand..."
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print 'OK'


def test_best_wild_hand():
    print "test_best_wild_hand..."
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print 'OK'


if __name__ == '__main__':
    test_best_hand()
    test_best_wild_hand()
