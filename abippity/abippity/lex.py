


def lex(text, verbose=False, syntax=False, file=None):
    state = 'newline'
    lexemes = []
    lexeme = ''

    if syntax:
        SINGLE_CHAR_LEXEMES = '()[]{}|.'
    else:
        SINGLE_CHAR_LEXEMES = '.,:'

    for i, c in enumerate(text):
        if verbose: print('{}'.format(repr(c)), file=file)
        while True:
            if verbose: print('  {}'.format(state), file=file)
            if state == 'newline':
                if c == '*': state = 'eat_comment'
                else: state = 'eat_whitespace'; continue
            elif state == 'eat_comment':
                if c == '\n': state = 'newline'
                else: pass
            elif state == 'eat_whitespace':
                if c == '\n': state = 'newline'
                elif c.isspace(): pass
                elif c in SINGLE_CHAR_LEXEMES: lexemes += c
                elif c == '"': state = 'eat_comment'
                elif c == '\'': lexeme += c; state = 'eat_char'
                elif c == '`': lexeme += c; state = 'eat_string'
                else: state = 'eat_word'; continue
            elif state == 'eat_char':
                if c == '\'': state = 'eat_char_escaped'
                else: lexeme += c
            elif state == 'eat_char_escaped':
                if c == '\'': lexeme += c; state = 'eat_char'
                else:
                    lexemes.append(lexeme)
                    lexeme = ''
                    state = 'eat_whitespace'
                    continue
            elif state == 'eat_string':
                if c == '`': state = 'eat_string_escaped'
                else: lexeme += c
            elif state == 'eat_string_escaped':
                if c == '`': lexeme += c; state = 'eat_string'
                else:
                    lexemes.append(lexeme)
                    lexeme = ''
                    state = 'eat_whitespace'
                    continue
            elif state == 'eat_word':
                if c.isspace() or c in SINGLE_CHAR_LEXEMES:
                    lexemes.append(lexeme)
                    lexeme = ''
                    state = 'eat_whitespace'
                    continue
                else: lexeme += c
            break

    if lexeme: lexemes.append(lexeme)
    return lexemes


def to_stmts(lexemes, syntax=False):
    stmts = []
    stmt = []
    chain_prefix = []

    for i, lexeme in enumerate(lexemes):
        if lexeme == ':':
            if chain_prefix:
                raise ValueError("Unexpected ':' "
                    "(can't have more than 1 in same statement)")
            chain_prefix = stmt
            stmt = []
        elif lexeme == ',' or lexeme == '.':
            if lexeme == ',' and not chain_prefix:
                raise ValueError("Unexpected ',' "
                    "(need to start a chained statement with ':')")
            stmts.append(chain_prefix + stmt)
            stmt = []
            if lexeme == '.':
                chain_prefix = []
        elif lexeme.startswith('\'') or lexeme.startswith('`'):
            stmt.append(lexeme)
        else:
            if syntax: stmt.append(lexeme)
            else: stmt.append(lexeme.lower())

    if chain_prefix or stmt:
        raise ValueError("Missing '.' at end of statement")

    return stmts

