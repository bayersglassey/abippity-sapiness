
from .lex import lex, to_stmts


def get_keywords():
    import os
    filepath = os.path.join(os.path.dirname(__file__), 'syntax.txt')
    with open(filepath) as f: text = f.read()
    lexemes = lex(text, syntax=True)
    stmts = to_stmts(lexemes, syntax=True)

    keywords = {}
    for stmt in stmts:
        keyword = stmt[0]
        syntax = []
        stack = []
        start = 0 if keyword.upper() == keyword else 1
        for lexeme in stmt[start:]:
            if lexeme == '{':
                stack.append(syntax)
                syntax = []
            elif lexeme == '}':
                syntax_part = syntax
                syntax = stack.pop()
                syntax.append(syntax_part)
            elif lexeme == '[':
                stack.append(syntax)
                syntax = []
            elif lexeme == ']':
                syntax_part = ('[', syntax)
                syntax = stack.pop()
                syntax.append(syntax_part)
            elif lexeme == '|':
                syntax_part = ('|', syntax.pop())
                syntax.append(syntax_part)
            else:
                syntax.append(lexeme)
        assert not stack
        keywords[keyword] = syntax
    return keywords


def print_syntax(syntax_part, depth=0):
    tabs = '  ' * depth
    if isinstance(syntax_part, tuple):
        kind = syntax_part[0]
        syntax = syntax_part[1]
        if kind == '[':
            print("{}[".format(tabs))
            print_syntax(syntax, depth+1)
            print("{}]".format(tabs))
        elif kind == '|':
            print_syntax(syntax, depth)
            print("{}|".format(tabs))
        else: raise ValueError("Unexpected kind: {}"
            .format(kind))
    elif isinstance(syntax_part, list):
        print("{}{}".format(tabs, '{'))
        for syntax in syntax_part:
            print_syntax(syntax, depth+1)
        print("{}{}".format(tabs, '}'))
    else:
        print("{}{}".format(tabs, syntax_part))


def parse(stmts, verbose=False, keywords=None):
    if keywords is None: keywords = get_keywords()
    parsed_stmts = []

    for i, stmt in enumerate(stmts):
        if '=' in stmt:
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
            print()
            print("STMT:   {}".format(stmt))
            print("SYNTAX: {}".format(syntax))

        ok, lexeme_i, captures = parse_stmt(stmt, 0, keywords, syntax,
            verbose=verbose, depth=1)
        if lexeme_i < len(stmt):
            raise ValueError("Couldn't parse entire stmt: {}".format(stmt))
        if not ok:
            raise ValueError("Couldn't parse stmt: {}".format(stmt))

        if verbose:
            print("CAPTURES: {}".format(captures))

        parsed_stmt = (keyword, captures)
        parsed_stmts.append(parsed_stmt)

    return parsed_stmts

def parse_stmt(stmt, lexeme_i, keywords, syntax_part,
        verbose=False, depth=0):
    """Returns (ok, lexeme_i, captures) where:
        ok - bool indicating whether stmt matches syntax
        lexeme_i - index in stmt of next lexeme
        captures - dict mapping parts of syntax to what they matched
            in the stmt
    """
    tabs = '  ' * depth
    captures = {}
    if verbose: print("{}->{} {}".format(
        tabs, syntax_part, stmt[lexeme_i:]))
    if isinstance(syntax_part, tuple):
        kind = syntax_part[0]
        sub_syntax = syntax_part[1]
        if kind == '[':
            ok, new_lexeme_i, sub_captures = parse_stmt(
                stmt, lexeme_i, keywords,
                sub_syntax, verbose, depth+1)
            if ok:
                lexeme_i = new_lexeme_i
                captures.update(sub_captures)
        elif kind == '|': pass
        else: raise ValueError("Unexpected kind: {}"
            .format(kind))
    elif isinstance(syntax_part, list):
        for sub_syntax in syntax_part:
            ok, lexeme_i, sub_captures = parse_stmt(
                stmt, lexeme_i, keywords,
                sub_syntax, verbose, depth+1)
            if not ok: return False, lexeme_i, captures
            captures.update(sub_captures)
    elif syntax_part[0] == '+' and syntax_part != '+':
        captures[syntax_part[1:]] = True
    else:
        is_keyword = syntax_part.upper() == syntax_part
        if is_keyword or syntax_part not in keywords:
            if lexeme_i >= len(stmt):
                return False, lexeme_i, captures
            lexeme = stmt[lexeme_i]
            lexeme_i += 1
            if is_keyword:
                if lexeme.upper() != syntax_part:
                    return False, lexeme_i, captures
                    raise ValueError("Expected {}, got: {}"
                        .format(syntax_part, lexeme))
            else:
                captures[syntax_part] = lexeme
        else:
            sub_syntax = keywords[syntax_part]
            ok, lexeme_i, sub_captures = parse_stmt(
                stmt, lexeme_i, keywords,
                sub_syntax, verbose, depth+1)
            if not ok: return False, lexeme_i, captures
            captures.update(sub_captures)
    return True, lexeme_i, captures
