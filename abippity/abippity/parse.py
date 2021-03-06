
import re
from .lex import lex, to_stmts
from .assertions import *


def isidentifier(s):
    return s and all(c == '_' or c.isalnum() for c in s)


def get_keywords_text():
    import os
    filepath = os.path.join(os.path.dirname(__file__), 'syntax.txt')
    with open(filepath) as f: text = f.read()
    return text

def get_keywords():
    text = get_keywords_text()
    lexemes = lex(text, syntax=True)
    stmts = to_stmts(lexemes, syntax=True)

    keywords = {}
    for stmt in stmts:
        keyword = stmt[0]
        syntax = []
        stack = []
        start = 0 if keyword.upper() == keyword else 1
        for lexeme in stmt[start:]:
            syntax_part = None
            if lexeme == '{':
                stack.append(syntax)
                syntax = []
            elif lexeme == '}':
                syntax_part = syntax
                syntax = stack.pop()
            elif lexeme == '[':
                stack.append(syntax)
                syntax = []
            elif lexeme == ']':
                syntax_part = ('[', syntax)
                syntax = stack.pop()
            elif lexeme == '|':
                syntax.append('|')
            elif lexeme.startswith('\''):
                syntax_part = lexeme[1:]
            else:
                syntax_part = lexeme

            if syntax_part is not None:
                while syntax and syntax[-1] == '|':
                    syntax.pop()
                    prev_syntax_part = syntax.pop()
                    syntax_part = ('|', prev_syntax_part, syntax_part)
                syntax.append(syntax_part)

        assertFalse(stack)
        if keyword in keywords:
            syntax = ('|', keywords[keyword], syntax)
        keywords[keyword] = syntax
    return keywords


def print_syntax(syntax_part, depth=0, file=None):
    tabs = '  ' * depth
    if isinstance(syntax_part, tuple):
        kind = syntax_part[0]
        if kind == '[':
            print("{}[".format(tabs), file=file)
            print_syntax(syntax_part[1], depth+1, file=file)
            print("{}]".format(tabs), file=file)
        elif kind == '|':
            print_syntax(syntax_part[1], depth, file=file)
            print("{}|".format(tabs), file=file)
            print_syntax(syntax_part[2], depth, file=file)
        else: raise ValueError("Unexpected kind: {}"
            .format(kind))
    elif isinstance(syntax_part, list):
        print("{}{}".format(tabs, '{'), file=file)
        for syntax in syntax_part:
            print_syntax(syntax, depth+1, file=file)
        print("{}{}".format(tabs, '}'), file=file)
    else:
        print("{}{}".format(tabs, syntax_part), file=file)

def print_keywords(keywords=None, file=None):
    print("KEYWORDS:", file=file)
    if keywords is None: keywords = get_keywords()
    for keyword, syntax in keywords.items():
        print(file=file)
        print("{}:".format(keyword), file=file)
        print_syntax(syntax, 1, file=file)


def parse(stmts, verbose=False, keywords=None, file=None):
    if keywords is None: keywords = get_keywords()
    parsed_stmts = []

    for i, stmt in enumerate(stmts):
        # if '=' in stmt:  # ????
        if '=' in stmt and stmt.index('=') == 1:
            index = stmt.index('=')
            lhs = stmt[:index]
            rhs = stmt[index+1:]
            captures = {'lhs': lhs, 'rhs': rhs}
            parsed_stmt = ('=', captures)
            parsed_stmts.append(parsed_stmt)
            continue
        keyword = stmt[0]
        syntax = keywords.get(keyword.upper())
        if syntax is None:
            raise ValueError("Invalid keyword: {}".format(keyword))

        if verbose:
            print(file=file)
            print("STMT:   {}".format(stmt), file=file)
            print("SYNTAX: {}".format(syntax), file=file)

        ok, lexeme_i, captures = parse_stmt(stmt, 0, keywords, syntax,
            verbose=verbose, depth=1, file=file)
        if lexeme_i < len(stmt):
            raise ValueError("Couldn't parse entire stmt: {}".format(stmt))
        if not ok:
            raise ValueError("Couldn't parse stmt: {}".format(stmt))

        if verbose:
            print("CAPTURES: {}".format(captures), file=file)

        parsed_stmt = (keyword, captures)
        parsed_stmts.append(parsed_stmt)

    return parsed_stmts

def parse_stmt(stmt, lexeme_i, keywords, syntax_part,
        verbose=False, depth=0, file=None):
    """Returns (ok, lexeme_i, captures) where:
        ok - bool indicating whether stmt matches syntax
        lexeme_i - index in stmt of next lexeme
        captures - dict mapping parts of syntax to what they matched
            in the stmt
    """
    tabs = '  ' * depth
    captures = {}
    if verbose: print("{}->{} {}".format(
        tabs, syntax_part, stmt[lexeme_i:]), file=file)
    if isinstance(syntax_part, tuple):
        kind = syntax_part[0]
        if kind == '[':
            sub_syntax = syntax_part[1]
            ok, new_lexeme_i, sub_captures = parse_stmt(
                stmt, lexeme_i, keywords,
                sub_syntax, verbose, depth+1, file=file)
            if ok:
                lexeme_i = new_lexeme_i
                captures.update(sub_captures)
        elif kind == '|':
            sub_syntax_a = syntax_part[1]
            sub_syntax_b = syntax_part[2]
            ok, new_lexeme_i, sub_captures = parse_stmt(
                stmt, lexeme_i, keywords,
                sub_syntax_a, verbose, depth+1, file=file)
            if ok:
                lexeme_i = new_lexeme_i
                captures.update(sub_captures)
            else:
                return parse_stmt(
                    stmt, lexeme_i, keywords,
                    sub_syntax_b, verbose, depth+1, file=file)
        else: raise ValueError("Unexpected kind: {}"
            .format(kind))
    elif isinstance(syntax_part, list):
        for sub_syntax in syntax_part:
            ok, lexeme_i, sub_captures = parse_stmt(
                stmt, lexeme_i, keywords,
                sub_syntax, verbose, depth+1, file=file)
            if not ok: return False, lexeme_i, captures
            captures.update(sub_captures)
    elif syntax_part[:1] == '+' and isidentifier(syntax_part[1:]):
        captures[syntax_part[1:]] = True
    else:
        is_named = ':' in syntax_part
        if is_named:
            capture_name, syntax_part = syntax_part.split(':')
        else:
            capture_name = syntax_part

        if syntax_part == '<at>':
            if not is_named: capture_name = 'at'

        is_many = syntax_part[-1:] == '+' and isidentifier(syntax_part[:-1])
        if is_many:
            syntax_part = syntax_part[:-1]
            if not is_named:
                # get rid of trailing '+'
                capture_name = syntax_part

        is_keyword = syntax_part.upper() == syntax_part

        if is_keyword or syntax_part not in keywords:
            if lexeme_i >= len(stmt):
                return False, lexeme_i, captures
            lexeme = stmt[lexeme_i]
            lexeme_i += 1
            if syntax_part == '<at>':
                match = re.fullmatch(
                    r'/?([0-9]+)?(\([0-9]+|(\*\*?)\))?', lexeme)
                if not match:
                    return False, lexeme_i, captures
                captures[capture_name] = lexeme
            elif is_keyword:
                if lexeme.upper() != syntax_part:
                    return False, lexeme_i, captures
            else:
                captures[capture_name] = lexeme
        elif is_many:
            sub_syntax = keywords[syntax_part]
            many_captures = []
            while True:
                ok, new_lexeme_i, sub_captures = parse_stmt(
                    stmt, lexeme_i, keywords,
                    sub_syntax, verbose, depth+1, file=file)
                if ok and sub_captures:
                    lexeme_i = new_lexeme_i
                    many_captures.append(sub_captures)
                else: break
            captures[capture_name] = many_captures
        else:
            sub_syntax = keywords[syntax_part]
            ok, lexeme_i, sub_captures = parse_stmt(
                stmt, lexeme_i, keywords,
                sub_syntax, verbose, depth+1, file=file)
            if not ok: return False, lexeme_i, captures
            if is_named: captures[capture_name] = sub_captures
            else: captures.update(sub_captures)
    return True, lexeme_i, captures



def group(parsed_stmts, verbose=False, file=None):
    grouped_stmts = []
    stack = [] # list of (parsed_stmt, grouped_stmts)
    for parsed_stmt in parsed_stmts:
        if verbose: print("grouping: {}".format(parsed_stmt), file=file)
        keyword, captures = parsed_stmt
        if keyword == 'if':
            if_parts = [captures.copy()]
            if_stmt = ('if', if_parts)
            stack.append((if_stmt, grouped_stmts))
            grouped_stmts = []
        elif keyword == 'elseif' or keyword == 'else' or keyword == 'endif':
            if_stmt, prev_grouped_stmts = stack.pop()
            if_keyword, if_parts = if_stmt
            if keyword == 'endif':
                assertIn(if_keyword, {'if', 'ifelse'})
            else:
                assertEqual(if_keyword, 'if')

            if_parts[-1]['block'] = grouped_stmts
            grouped_stmts = []

            if keyword != 'endif':
                if_parts.append(captures.copy())

            new_if_keyword = 'ifelse' if keyword == 'else' else 'if'
            new_if_stmt = (new_if_keyword, if_parts)

            if keyword == 'endif':
                grouped_stmts = prev_grouped_stmts
                grouped_stmts.append(new_if_stmt)
            else:
                stack.append((new_if_stmt, prev_grouped_stmts))
        elif keyword == 'data' and 'begin' in captures:
            data_stmt = ('data_begin', captures.copy())
            stack.append((data_stmt, grouped_stmts))
            grouped_stmts = []
        elif keyword == 'data' and 'end' in captures:
            data_stmt, prev_grouped_stmts = stack.pop()
            data_keyword, data_captures = data_stmt
            assertEqual(data_keyword, 'data_begin')
            assertEqual(captures['struc'], data_captures['struc'])
            data_captures['block'] = grouped_stmts
            grouped_stmts = prev_grouped_stmts
            grouped_stmts.append(data_stmt)
        elif keyword in {'while', 'do'}:
            new_stmt = (keyword, captures.copy())
            stack.append((new_stmt, grouped_stmts))
            grouped_stmts = []
        elif keyword in {'endwhile', 'enddo'}:
            new_stmt, prev_grouped_stmts = stack.pop()
            new_keyword, new_captures = new_stmt
            assertEqual(new_keyword,
                {'endwhile': 'while', 'enddo': 'do'}[keyword])
            new_captures['block'] = grouped_stmts
            grouped_stmts = prev_grouped_stmts
            grouped_stmts.append(new_stmt)
        else:
            grouped_stmt = parsed_stmt
            grouped_stmts.append(grouped_stmt)
    assertFalse(stack)
    return grouped_stmts

def print_grouped_stmts(grouped_stmts, depth=0, file=None):
    tabs = '  ' * depth
    for grouped_stmt in grouped_stmts:
        keyword, captures = grouped_stmt
        if keyword in {'if', 'case'}:
            parts = captures
            print("{}{}".format(tabs, keyword), file=file)
            for part in parts:
                captures = part.copy()
                block = captures.pop('block')
                print("{}->{}".format(tabs, captures), file=file)
                print_grouped_stmts(block, depth+1, file=file)
        elif 'block' in captures:
            captures = captures.copy()
            block = captures.pop('block')
            print("{}{} -> {}".format(tabs, keyword, captures), file=file)
            print_grouped_stmts(block, depth+1, file=file)
        else:
            print("{}{} -> {}".format(tabs, keyword, captures), file=file)

