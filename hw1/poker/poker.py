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

TWO_JOKER = 3
BLACK_JOKER = 2
RED_JOKER = 1
NO_JOKER = 0

BLACK_JOKER_SYMBOL = '?B'
RED_JOKER_SYMBOL = '?R'

helper_symbol_ranks = '23456789TJQKA'
helper_black_suits = 'CS'
helper_red_suits = 'HD'
helper_letters = dict(zip(helper_symbol_ranks, range(2, 16)))  # map ranks to int
helper_ranks = '14 13 12 11 10 9 8 7 6 5 4 3 2'
helper_lowest_straight = '14 5 4 3 2'  # straight can start with A


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
    ranks = sorted([helper_letters.get(el[0]) for el in hand], reverse=True)
    return ranks


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    suits = [el[1] for el in hand]
    counts = collections.Counter(suits)
    val = max(counts.values())
    return val == 5


def straight(ranks):
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)

    Alexey notes: я бы в эту функцию передавал не ранги а hand, получилось бы красивее.
    Т.е. helper_ranks бы поменялась на A 2 3 4 5 6 7 8 9 T J Q K A и так же проверял бы на вхождение
    отсортировонной руки в строке через in.
    """
    inner_seq = ' '.join(str(el) for el in ranks)
    return inner_seq in helper_ranks or inner_seq in helper_lowest_straight


def _find_equal_n(n, ranks):
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
    all_ranks = [hand_rank(el) for el in five_cards_hands]
    m = max(all_ranks)
    ix = all_ranks.index(m)
    return sorted(list(five_cards_hands[ix]))


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    all_ranks = []
    five_cards_hands = itertools.combinations(hand, 5)
    for comb in five_cards_hands:
        joker_type = _get_joker_type(comb)
        if joker_type == BLACK_JOKER:
            black_ix = comb.index(BLACK_JOKER_SYMBOL)
            for replacement in _get_black_joker_replacement(comb):
                new_hand = list(copy.copy(comb))
                new_hand[black_ix] = replacement
                rank = hand_rank(new_hand)
                all_ranks.append((rank, new_hand))
        elif joker_type == RED_JOKER_SYMBOL:
            red_ix = comb.index(RED_JOKER_SYMBOL)
            for replacement in _get_red_joker_replacement(comb):
                new_hand = list(copy.copy(comb))
                new_hand[red_ix] = replacement
                rank = hand_rank(new_hand)
                all_ranks.append((rank, new_hand))
        elif joker_type == TWO_JOKER:
            black_ix = comb.index(BLACK_JOKER_SYMBOL)
            red_ix = comb.index(RED_JOKER_SYMBOL)
            for replacement in _get_all_replacements(comb):
                new_hand = list(copy.copy(comb))
                new_hand[black_ix] = replacement[0]
                new_hand[red_ix] = replacement[1]
                rank = hand_rank(new_hand)
                all_ranks.append((rank, new_hand))
        else:
            all_ranks.append((hand_rank(comb), comb))
    m = max(all_ranks, key=lambda x: x[0])
    result = sorted(m[1])
    return result


def _get_black_joker_replacement(hand):
    return set(rank + suit for rank in helper_symbol_ranks for suit in helper_black_suits) - set(hand)


def _get_red_joker_replacement(hand):
    return set(rank + suit for rank in helper_symbol_ranks for suit in helper_red_suits) - set(hand)


def _get_all_replacements(hand):
    return ((black, red) for black in _get_black_joker_replacement(hand) for red in _get_red_joker_replacement(hand))


def _get_joker_type(hand):
    if BLACK_JOKER_SYMBOL in hand and RED_JOKER_SYMBOL in hand:
        return TWO_JOKER
    elif BLACK_JOKER_SYMBOL in hand:
        return BLACK_JOKER
    elif RED_JOKER_SYMBOL in hand:
        return RED_JOKER
    else:
        return NO_JOKER


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
