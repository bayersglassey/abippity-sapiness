#!/bin/env python

from sys import stdin, stdout, argv
from lib.parse import lex, to_stmts, get_keywords
from lib.run import run

if __name__ == '__main__':
    text = stdin.read()
    args = argv[1:]

    PRINT_KEYWORDS = '--keywords' in args
    LEX_VERBOSE = '--lex-verbose' in args
    LEX_SYNTAX = '--lex-syntax' in args
    PRINT_LEXEMES = '--lexemes' in args
    PRINT_STMTS = '--stmts' in args
    RUN = '--run' in args
    RUN_VERBOSE = '--run-verbose' in args
    PRINT_REPORT = '--report' in args
    PRINT_VARS = '--vars' in args

    keywords = get_keywords()
    if PRINT_KEYWORDS:
        for name, stmt in keywords.items():
            print("{}: {}".format(name, stmt))

    lexemes = lex(text, verbose=LEX_VERBOSE, syntax=LEX_SYNTAX)
    if PRINT_LEXEMES:
        for lexeme in lexemes:
            print(lexeme)

    stmts = to_stmts(lexemes)
    if PRINT_STMTS:
        for stmt in stmts:
            print(stmt)

    if RUN:
        report, vars = run(stmts, 40, 20, verbose=RUN_VERBOSE)
        if PRINT_REPORT:
            report.print()
        if PRINT_VARS:
            for varname, value in vars.items():
                print('{}: {}'.format(varname, repr(value)))
