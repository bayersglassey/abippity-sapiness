#!/bin/env python

from .lib.lex import lex, to_stmts
from .lib.parse import (get_keywords, print_syntax, parse, group,
    print_grouped_stmts)
from .lib.run import Runner

OPTIONS = [
    # general
    ('PRINT_KEYWORDS', '--keywords'),

    # lexing arguments
    ('LEX', '--lex'),
    ('LEX_VERBOSE', '--lex-verbose'),
    ('LEX_SYNTAX', '--lex-syntax'),
    ('PRINT_LEXEMES', '--lexemes'),
    ('PRINT_STMTS', '--stmts'),

    # parsing options
    ('PARSE', '--parse'),
    ('PARSE_VERBOSE', '--parse-verbose'),
    ('PRINT_PARSED_STMTS', '--parsed-stmts'),

    # grouping options
    ('GROUP', '--group'),
    ('GROUP_VERBOSE', '--group-verbose'),
    ('PRINT_GROUPED_STMTS', '--grouped-stmts'),

    # running arguments
    ('RUN', '--run'),
    ('RUN_VERBOSE', '--run-verbose'),
    ('PRINT_REPORT', '--report'),
    ('PRINT_VARS', '--vars'),
    ('VERBOSE_BOOLS', '--verbose-bools'),
]




def parse_options(args):
    options = {}
    for name, arg in OPTIONS:
        options[name] = arg in args
    return options


def main(text, options, keywords=None, file=None):

    # option chaining
    RUN = options.get('RUN')
    GROUP = RUN or options.get('GROUP')
    PARSE = GROUP or options.get('PARSE')
    LEX = PARSE or options.get('RUN')

    # get keywords
    if keywords is None: keywords = get_keywords()
    if options.get('PRINT_KEYWORDS'):
        print("KEYWORDS:", file=file)
        for keyword, syntax in keywords.items():
            print(file=file)
            print("{}:".format(keyword), file=file)
            print_syntax(syntax, 1, file=file)

    if LEX:
        # lex text into lexemes
        lexemes = lex(text, verbose=options.get('LEX_VERBOSE'),
            syntax=options.get('LEX_SYNTAX'))
        if options.get('PRINT_LEXEMES'):
            for lexeme in lexemes:
                print(lexeme, file=file)


    if PARSE:
        # get stmts (lists of lexemes representing ABAP commands)
        stmts = to_stmts(lexemes)
        if options.get('PRINT_STMTS'):
            for stmt in stmts:
                print(stmt, file=file)

        # parse stmts (transform lists of lexemes into pairs of
        # (keyword:str, captures:dict))
        parsed_stmts = parse(stmts,
            verbose=options.get('PARSE_VERBOSE'))
        if options.get('PRINT_PARSED_STMTS'):
            print("PARSED STATEMENTS:", file=file)
            for parsed_stmt in parsed_stmts:
                print(parsed_stmt, file=file)

    if GROUP:
        # group stmts (stick groups of stmts inside other stmt's captures,
        # forming a hierarchy of blocks of code)
        grouped_stmts = group(parsed_stmts,
            verbose=options.get('GROUP_VERBOSE'), file=file)
        if options.get('PRINT_GROUPED_STMTS'):
            print("GROUPED STATEMENTS:", file=file)
            print_grouped_stmts(grouped_stmts, 1, file=file)

    if RUN:
        # run grouped stmts
        runner = Runner(40, 20,
            verbose=options.get('RUN_VERBOSE'),
            verbose_bools=options.get('VERBOSE_BOOLS'),
            file=file)
        report = runner.run(grouped_stmts, toplevel=True)
        if options.get('PRINT_REPORT'):
            report.print(file=file)
        if options.get('PRINT_VARS'):
            for var in runner.vars.values():
                print("{}".format(var), file=file)



if __name__ == '__main__':
    from sys import stdin, stdout, argv
    text = stdin.read()
    args = argv[1:]
    options = parse_options(args)
    main(text, options)
