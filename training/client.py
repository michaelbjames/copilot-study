#!/usr/bin/env python3
import sys



"""
Does your usual setup include some python checking plugins?

They should find an error in the following code:
"""
def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        # fib_dne is not defined, and should get some kind of squiggle or mark
        return fib_dne(n - 1) + fib(n - 2)