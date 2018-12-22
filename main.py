#!/bin/env python

from sys import stdin, stdout
from lib.abap import lex

if __name__ == '__main__':
    text = stdin.read()
    lexemes = lex(text, verbose=True)
    print('\n'.join(lexemes))

