
KEYWORDS = {'report', 'write', 'skip', 'uline', 'data', 'move',
    'constants', 'types', 'message'}
TYPES = {'x', 'c', 'n', 'd', 't', 'i', 'f', 'p', 'string', 'xstring'}


class Screen:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.data = [[' '] * w for i in range(h)]
        self.x = 0
        self.y = 0
    def putc(self, c):
        self.data[self.y][self.x] = c
        self.spacebar()
    def puts(self, text):
        for c in text: self.putc(c)
    def spacebar(self):
        self.x += 1
        if self.x >= self.w: self.newline()
    def newline(self):
        self.x = 0
        self.y += 1
        if self.y >= self.h:
            self.h += 1
            self.data.append([' '] * self.w)
    def as_lines(self):
        return [''.join(line_data) for line_data in self.data]

class Report:
    def __init__(self, title, screen):
        self.title = title
        self.screen = screen
    def print(self):
        print("REPORT: {}".format(self.title.upper()))
        screen = self.screen
        uline = '*' * screen.w
        print(uline)
        for line in screen.as_lines():
            print(line)
        print(uline)


def parse_value(text, vars):
    if text.startswith('\''):
        return text[1:]
    return vars[text]


def run(stmts, w=80, h=40, verbose=False):
    report_title = ''
    screen = Screen(w, h)
    vars = {}

    if not stmts:
        raise ValueError("Empty report!")

    for i, stmt in enumerate(stmts):
        if verbose: print(stmt)
        if not stmt:
            raise ValueError("Empty statement!")
        if len(stmt) >= 2 and stmt[1] == '=':
            stmt = ['move'] + stmt[2:] + ['to', stmt[0]]

        keyword = stmt[0]
        if keyword not in KEYWORDS:
            raise ValueError("Invalid keyword: {}".format(keyword))
        if (i == 0) != (keyword == 'report'):
            if keyword == 'report':
                raise ValueError("Unexpected 'report' "
                    "(should come exactly once, at top of file)")
            else:
                raise ValueError("Missing 'report' "
                    "(should come exactly once, at top of file)")

        if keyword == 'data':
            varname = stmt[1]
            vars[varname] = None
        elif keyword == 'move':
            value = parse_value(stmt[1], vars)
            assert stmt[2] == 'to'
            varname = stmt[3]
            vars[varname] = value
        elif keyword == 'write':
            for lexeme in stmt[1:]:
                if lexeme == '/':
                    screen.newline()
                else:
                    value = parse_value(lexeme, vars)
                    screen.puts(value)
        elif keyword == 'skip':
            x = 0
            y += 1
        elif keyword == 'report':
            assert len(stmt) == 2
            report_title = stmt[1]
        else:
            raise ValueError('Keyword not implemented: {}'
                .format(keyword))

    report = Report(report_title, screen)
    return report, vars
