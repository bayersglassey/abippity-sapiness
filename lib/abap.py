

SINGLE_CHAR_LEXEMES = '.,:'
KEYWORDS = {'write', 'types'}


def lex(text, verbose=False):
    state = 'newline'
    lexemes = []
    lexeme = ''

    for i, c in enumerate(text):
        if verbose: print('{}'.format(repr(c)))
        while True:
            if verbose: print('  {}'.format(state))
            if state is 'newline':
                if c is '*': state = 'eat_comment'
                else: state = 'eat_whitespace'; continue
            elif state is 'eat_comment':
                if c is '\n': state = 'newline'
                else: pass
            elif state is 'eat_whitespace':
                if c is '\n': state = 'newline'
                elif c.isspace(): pass
                elif c in SINGLE_CHAR_LEXEMES: lexemes += c
                elif c is '"': state = 'eat_comment'
                elif c is '\'': lexeme += c; state = 'eat_string'
                elif c.isdigit(): state = 'eat_num'; continue
                elif c is '_' or c.isalpha(): state = 'eat_word'; continue
                elif c.isprintable(): state = 'eat_op'; continue
                else: raise ValueError("Weird character: {} (ord={})"
                    .format(c, ord(c)))
            elif state is 'eat_string':
                if c is '\n':
                    raise ValueError("Unterminated string literal")
                elif c is '\'':
                    lexemes.append(lexeme)
                    lexeme = ''
                    state = 'eat_whitespace'
                else:
                    lexeme += c
            elif state is 'eat_num':
                if c.isdigit():
                    lexeme += c
                else:
                    lexemes.append(lexeme)
                    lexeme = ''
                    state = 'eat_whitespace'
                    continue
            elif state is 'eat_word':
                if c is '_' or c.isalnum():
                    lexeme += c
                else:
                    lexemes.append(lexeme)
                    lexeme = ''
                    state = 'eat_whitespace'
                    continue
            elif state is 'eat_op':
                if c.isprintable() and not(
                    c in SINGLE_CHAR_LEXEMES or c is '_' or c.isalnum()
                ):
                    lexeme += c
                else:
                    lexemes.append(lexeme)
                    lexeme = ''
                    state = 'eat_whitespace'
                    continue
            break

    if lexeme: lexemes.append(lexeme)
    return lexemes


def fmt_stmt(stmt): return ' '.join(stmt)

def to_stmts(lexemes):
    stmts = []
    stmt_lexemes = []
    keyword = ''
    is_chained = False

    for i, lexeme in enumerate(lexemes):
        if not keyword:
            keyword = lexeme.lower()
            if keyword not in KEYWORDS:
                raise ValueError("Invalid keyword: {}".format(keyword))
        elif lexeme is ':':
            if stmt_lexemes:
                raise ValueError("Unexpected ':' "
                    "(must immediately follow keyword)")
            is_chained = True
        elif lexeme is ',' or lexeme is '.':
            if lexeme is ',' and not is_chained:
                raise ValueError("Unexpected ',' "
                    "(keyword must be followed by ':' to start a "
                    "chained statement)")
            stmt = [keyword] + stmt_lexemes
            stmts.append(stmt)
            del stmt
            stmt_lexemes = []
            if lexeme is '.':
                keyword = ''
                is_chained = False
        else: stmt_lexemes.append(lexeme)

    if stmt_lexemes:
        raise ValueError("Missing '.' at end of statement")

    return stmts


class Parser:

    def __init__(self, text):
        self.text = text
        self.lexemes = lex(text)
        self.stmts = to_stmts(self.lexemes)

