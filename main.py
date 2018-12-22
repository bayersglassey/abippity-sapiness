#!/bin/env python

from sys import stdin, stdout
from lib.parse import lex, to_stmts
from lib.run import run

if __name__ == '__main__':
    text = stdin.read()

    PRINT_LEXEMES = False
    PRINT_STMTS = False
    PRINT_REPORT = True
    PRINT_VARS = True

    lexemes = lex(text)
    if PRINT_LEXEMES:
        for lexeme in lexemes:
            print(lexeme)

    stmts = to_stmts(lexemes)
    if PRINT_STMTS:
        for stmt in stmts:
            print(stmt)

    report, vars = run(stmts, 40, 20, verbose=True)
    if PRINT_REPORT:
        report.print()
    if PRINT_VARS:
        for varname, value in vars.items():
            print('{}: {}'.format(varname, repr(value)))
