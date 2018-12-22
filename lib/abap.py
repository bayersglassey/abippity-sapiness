

def lex(text, verbose=False):
    state = 'newline'
    lexemes = []
    lexeme = ''

    SINGLETONS = '.,:\''

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
                elif c is '"': state = 'eat_comment'
                elif c in SINGLETONS: lexemes += c
                elif c.isdigit(): state = 'eat_num'; continue
                elif c is '_' or c.isalpha(): state = 'eat_word'; continue
                elif c.isprintable(): state = 'eat_op'; continue
                else: raise ValueError("Weird character: {} (ord={})"
                    .format(c, ord(c)))
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
                    c in SINGLETONS or c is '_' or c.isalnum()
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


class Parser:

    def __init__(self, text):
        self.text = text
        self.lexemes = lex(text)

