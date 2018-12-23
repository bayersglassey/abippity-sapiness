#!/bin/env python

from sys import stdin, stdout, argv
from lib.lex import lex, to_stmts
from lib.parse import get_keywords, print_syntax, parse
from lib.run import run

if __name__ == '__main__':
    text = stdin.read()
    args = argv[1:]

    PRINT_KEYWORDS = '--keywords' in args

    # lexing arguments
    LEX_VERBOSE = '--lex-verbose' in args
    LEX_SYNTAX = '--lex-syntax' in args
    PRINT_LEXEMES = '--lexemes' in args
    PRINT_STMTS = '--stmts' in args

    # parsing options
    PARSE = '--parse' in args
    PARSE_VERBOSE = '--parse-verbose' in args
    PRINT_PARSED_STMTS = '--parsed-stmts' in args

    # running arguments
    RUN = '--run' in args
    RUN_VERBOSE = '--run-verbose' in args
    PRINT_REPORT = '--report' in args
    PRINT_VARS = '--vars' in args

    # get keywords
    keywords = get_keywords()
    if PRINT_KEYWORDS:
        print("KEYWORDS:")
        for keyword, syntax in keywords.items():
            print()
            print("{}:".format(keyword))
            print_syntax(syntax, 1)

    # lex text into lexemes
    lexemes = lex(text, verbose=LEX_VERBOSE, syntax=LEX_SYNTAX)
    if PRINT_LEXEMES:
        for lexeme in lexemes:
            print(lexeme)

    # get stmts from lexemes
    stmts = to_stmts(lexemes)
    if PRINT_STMTS:
        for stmt in stmts:
            print(stmt)

    # parse & run
    if RUN: PARSE = True
    if PARSE:
        # parse stmts
        parsed_stmts = parse(stmts, verbose=PARSE_VERBOSE)
        if PRINT_PARSED_STMTS:
            print("PARSED STATEMENTS:")
            for parsed_stmt in parsed_stmts:
                print(parsed_stmt)

        # run parsed stmts
        if RUN:
            report, vars = run(parsed_stmts, 40, 20, verbose=RUN_VERBOSE)
            if PRINT_REPORT:
                report.print()
            if PRINT_VARS:
                for varname, value in vars.items():
                    print('{}: {}'.format(varname, repr(value)))
