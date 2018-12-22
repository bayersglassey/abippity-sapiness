#!/bin/env python

from sys import stdin, stdout
from lib.abap import lex, to_stmts

if __name__ == '__main__':
    text = stdin.read()

    lexemes = lex(text, verbose=True)
    for lexeme in lexemes:
        print(lexeme)

    stmts = to_stmts(lexemes)
    for stmt in stmts:
        print(stmt)

