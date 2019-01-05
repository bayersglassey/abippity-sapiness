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

    # basic parsing
    options = {}
    for name, arg in OPTIONS:
        options[name] = arg in args

    # option chaining
    if options['RUN']:
        options['GROUP'] = True
    if options['GROUP']:
        options['PARSE'] = True
    if options['PARSE']:
        options['LEX'] = True

    return options


def main(text, options, keywords=None):

    # get keywords
    if keywords is None: keywords = get_keywords()
    if options['PRINT_KEYWORDS']:
        print("KEYWORDS:")
        for keyword, syntax in keywords.items():
            print()
            print("{}:".format(keyword))
            print_syntax(syntax, 1)

    # lex text into stmts
    if options['LEX']:
        # lex text into lexemes
        lexemes = lex(text, verbose=options['LEX_VERBOSE'],
            syntax=options['LEX_SYNTAX'])
        if options['PRINT_LEXEMES']:
            for lexeme in lexemes:
                print(lexeme)

        # get stmts from lexemes
        stmts = to_stmts(lexemes)
        if options['PRINT_STMTS']:
            for stmt in stmts:
                print(stmt)

    # parse & group & run
    if options['PARSE']:
        # parse stmts
        parsed_stmts = parse(stmts, verbose=options['PARSE_VERBOSE'])
        if options['PRINT_PARSED_STMTS']:
            print("PARSED STATEMENTS:")
            for parsed_stmt in parsed_stmts:
                print(parsed_stmt)

        if options['GROUP']:
            # group stmts
            grouped_stmts = group(parsed_stmts,
                verbose=options['GROUP_VERBOSE'])
            if options['PRINT_GROUPED_STMTS']:
                print("GROUPED STATEMENTS:")
                print_grouped_stmts(grouped_stmts, 1)

            # run grouped stmts
            if options['RUN']:
                runner = Runner(40, 20, verbose=options['RUN_VERBOSE'],
                    verbose_bools=options['VERBOSE_BOOLS'])
                report = runner.run(grouped_stmts, toplevel=True)
                if options['PRINT_REPORT']:
                    report.print()
                if options['PRINT_VARS']:
                    for var in runner.vars.values():
                        print("{}".format(var))



if __name__ == '__main__':
    from sys import stdin, stdout, argv
    text = stdin.read()
    args = argv[1:]
    options = parse_options(args)
    main(text, options)
