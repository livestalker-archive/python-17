#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import update_wrapper


def disable(f):
    """
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    """
    return f


def decorator(dec):
    """
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    """

    def decorated(f):
        res = dec(f)
        return update_wrapper(res, f)

    return decorated


@decorator
def countcalls(f):
    """Decorator that counts calls made to the function decorated."""

    def counted(*args):
        counted.calls += 1
        return f(*args)

    counted.calls = 0
    return counted


@decorator
def memo(f):
    """
    Memoize a function so that it caches all return values for
    faster future lookups.
    """
    cache = {}

    def memorized(*args):
        res_key = tuple(args)
        if res_key not in cache:
            res = f(*args)
            cache[res_key] = res
            update_wrapper(memorized, f)
            return res
        else:
            return cache[res_key]

    return memorized


@decorator
def n_ary(f):
    """
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    """

    def complex_func(*args):
        if len(args) == 1:
            return args[0]
        else:
            return f(args[0], complex_func(*args[1:]))

    return complex_func


def trace(fill):
    """Trace calls made to function decorated.

    @trace("____")
    def fib(n):
        ....

    >>> fib(3)
     --> fib(3)
    ____ --> fib(2)
    ________ --> fib(1)
    ________ <-- fib(1) == 1
    ________ --> fib(0)
    ________ <-- fib(0) == 1
    ____ <-- fib(2) == 2
    ____ --> fib(1)
    ____ <-- fib(1) == 1
     <-- fib(3) == 3

    """

    @decorator
    def trace_decorator(f):
        def traced(*args):
            prefix = fill * traced.depth
            arg_str = ", ".join(str(a) for a in args)
            print "{} --> {}({})".format(prefix, f.__name__, arg_str)
            traced.depth += 1
            result = f(*args)
            print "{} <-- {}({}) == {}".format(prefix, f.__name__, arg_str, result)
            traced.depth -= 1
            return result
        traced.depth = 0
        return traced
    return trace_decorator


@memo
@countcalls
@n_ary
def foo(a, b):
    """a+b"""
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    """a*b"""
    return a * b


@countcalls
@trace("####")
@memo
def fib(n):
    """fib"""
    return 1 if n <= 1 else fib(n - 1) + fib(n - 2)


def main():
    print foo(4, 3)
    print foo(4, 3, 2)
    print foo(4, 3)
    print "foo was called", foo.calls, "times"

    print bar(4, 3)
    print bar(4, 3, 2)
    print bar(4, 3, 2, 1)
    print "bar was called", bar.calls, "times"

    print fib.__doc__
    fib(3)
    print fib.calls, 'calls made'


if __name__ == '__main__':
    main()
