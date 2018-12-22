

SINGLE_CHAR_LEXEMES = '.,:'
KEYWORDS = {'report', 'write', 'skip', 'uline', 'data', 'move',
    'constants', 'types', 'message'}
TYPES = {'x', 'c', 'n', 'd', 't', 'i', 'f', 'p', 'string', 'xstring'}


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
                else: state = 'eat_word'; continue
            elif state is 'eat_string':
                if c is '\'':
                    lexemes.append(lexeme)
                    lexeme = ''
                    state = 'eat_whitespace'
                else:
                    lexeme += c
            elif state is 'eat_word':
                if c.isspace() or c in SINGLE_CHAR_LEXEMES:
                    lexemes.append(lexeme)
                    lexeme = ''
                    state = 'eat_whitespace'
                    continue
                else: lexeme += c
            break

    if lexeme: lexemes.append(lexeme)
    return lexemes


def to_stmts(lexemes):
    stmts = []
    stmt = []
    chain_prefix = []

    for i, lexeme in enumerate(lexemes):
        if lexeme is ':':
            if chain_prefix:
                raise ValueError("Unexpected ':' "
                    "(can't have more than 1 in same statement)")
            chain_prefix = stmt
            stmt = []
        elif lexeme is ',' or lexeme is '.':
            if lexeme is ',' and not chain_prefix:
                raise ValueError("Unexpected ',' "
                    "(need to start a chained statement with ':')")
            stmts.append(chain_prefix + stmt)
            stmt = []
            if lexeme is '.':
                chain_prefix = []
        elif lexeme.startswith('\''): stmt.append(lexeme)
        else: stmt.append(lexeme.lower())

    if chain_prefix or stmt:
        raise ValueError("Missing '.' at end of statement")

    return stmts


class Parser:

    def __init__(self, text):
        self.text = text
        self.lexemes = lex(text)
        self.stmts = to_stmts(self.lexemes)

