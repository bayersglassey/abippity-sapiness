
import re

BASETYPES = {'x', 'c', 'n', 'd', 't', 'i', 'f', 'p', 'string', 'xstring'}


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
    def put_value(self, value):
        self.puts(value.to_text())
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


_types = {}
class Type:
    def __init__(self, basetype):
        assert basetype in BASETYPES
        self.basetype = basetype
    def __str__(self):
        return "{}".format(self.basetype)
    def __repr__(self):
        return "Type({})".format(self)
    def __eq__(self, other):
        return self.basetype == other.basetype
    @classmethod
    def from_text(Type, text):
        if text in _types:
            return _types[text]
        return Type(text)
    def get_initial(self):
        """Returns the \"initial\" value for the given ABAP type
        (that is, the value for which the ABAP expression
        \"<value> IS INITIAL\" is true)"""
        basetype = self.basetype
        if basetype == 'n':
            return Value(self, 0)
        elif basetype == 'string':
            return Value(self, "")
        else:
            raise ValueError("Not implemented for type: {}"
                .format(self))

class Value:
    def __init__(self, type, data):
        self.type = type
        self.data = data
    def __str__(self):
        return str(self.data)
    def __repr__(self):
        return "Value({} TYPE {})".format(self.data, self.type)
    def to_text(self):
        return str(self.data)
    @classmethod
    def from_text(Value, text):
        c0 = text[0:1]
        if c0 == '\'':
            return Value(Type.from_text('string'), text[1:])
        if c0.isdigit():
            return Value(Type.from_text('n'), int(text))
        raise ValueError("Can't parse value from text: {}"
            .format(repr(text)))

class Var:
    def __init__(self, name, type, dims=None, value=None):
        self.name = name.lower()
        self.type = type
        self.dims = dims
        if value is None:
            value = type.get_initial()
        self.set(value)
    def __str__(self):
        s = "{}".format(self.name)
        if self.dims is not None:
            s = "{}({})".format(s, self.dims)
        return "{} TYPE {} VALUE {}".format(s, self.type, self.value)
    def __repr__(self):
        return "Var({})".format(self)
    def get(self):
        return self.value
    def set(self, value):
        assert self.type == value.type
        self.value = value

class Ref:
    def __init__(self, var):
        self.var = var
    def __str__(self):
        return "REF TO {}".format(self.var)
    def __repr__(self):
        return "Ref({})".format(self)
    def get(self):
        return self.var.get()
    def set(self, value):
        self.var.set(value)

def parse_var(text):
    match = re.fullmatch(r'(?P<name>[a-zA-Z_][a-zA-Z_0-9]*)(\((?P<dims>[0-9]+)\))?', text)
    groupdict = match.groupdict()
    name = groupdict['name']
    dims = groupdict['dims']
    if dims: dims = int(dims)
    return name, dims

def parse_value(text, vars):
    c0 = text[0:1]
    if c0 == '\'' or c0.isdigit():
        return Value.from_text(text)
    return vars[text].get()

def parse_ref(text, vars):
    return Ref(vars[text])



def run(parsed_stmts, w=80, h=40, verbose=False):
    report_title = ''
    screen = Screen(w, h)
    vars = {}

    if not parsed_stmts:
        raise ValueError("Empty report!")

    for i, parsed_stmt in enumerate(parsed_stmts):
        if verbose: print("Running: {}".format(parsed_stmt))
        keyword, captures = parsed_stmt

        if (i == 0) != (keyword == 'report'):
            if keyword == 'report':
                raise ValueError("Unexpected 'report' "
                    "(should come exactly once, at top of file)")
            else:
                raise ValueError("Missing 'report' "
                    "(should come exactly once, at top of file)")

        if keyword == 'data':
            var_text = captures['var']
            type_text = captures['abap_type']
            name, dims = parse_var(var_text)
            type = Type.from_text(type_text)
            var = Var(name, type, dims)
            vars[name] = var
        elif keyword == 'move':
            src_text = captures['source']
            dest_text = captures['destination']
            src = parse_value(src_text, vars)
            dest = parse_ref(dest_text, vars)
            dest.set(src)
        elif keyword == 'write':
            if 'newline' in captures:
                screen.newline()
            dobj = captures['dobj']
            value = parse_value(dobj, vars)
            screen.put_value(value)
            if 'nogap' not in captures:
                screen.spacebar()
        elif keyword == 'skip':
            to_line = captures.get('line')
            if to_line is not None:
                raise NotImplemented("SKIP TO LINE")
            else:
                n = captures.get('n', 1)
                for i in range(n):
                    screen.newline()
        elif keyword == 'report':
            report_title = captures['rep']
        else:
            raise ValueError('Keyword not implemented: {}'
                .format(keyword))

    report = Report(report_title, screen)
    return report, vars
