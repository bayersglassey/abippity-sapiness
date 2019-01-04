#!/bin/env python

from sys import stdin, stdout, argv
from lib.lex import lex, to_stmts
from lib.parse import (get_keywords, print_syntax, parse, group,
    print_grouped_stmts)
from lib.run import Runner

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

    # grouping options
    GROUP = '--group' in args
    GROUP_VERBOSE = '--group-verbose' in args
    PRINT_GROUPED_STMTS = '--grouped-stmts' in args

    # running arguments
    RUN = '--run' in args
    RUN_VERBOSE = '--run-verbose' in args
    PRINT_REPORT = '--report' in args
    PRINT_VARS = '--vars' in args
    VERBOSE_BOOLS = '--verbose-bools' in args

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

    # parse & group & run
    if RUN:
        PARSE = True
    if PARSE:
        GROUP = True
    if PARSE:
        # parse stmts
        parsed_stmts = parse(stmts, verbose=PARSE_VERBOSE)
        if PRINT_PARSED_STMTS:
            print("PARSED STATEMENTS:")
            for parsed_stmt in parsed_stmts:
                print(parsed_stmt)

        if GROUP:
            # group stmts
            grouped_stmts = group(parsed_stmts, verbose=GROUP_VERBOSE)
            if PRINT_GROUPED_STMTS:
                print("GROUPED STATEMENTS:")
                print_grouped_stmts(grouped_stmts, 1)

            # run grouped stmts
            if RUN:
                runner = Runner(40, 20, verbose=RUN_VERBOSE,
                    verbose_bools=VERBOSE_BOOLS)
                report = runner.run(grouped_stmts)
                if PRINT_REPORT:
                    report.print()
                if PRINT_VARS:
                    for varname, value in runner.vars.items():
                        print("{}".format(value))
