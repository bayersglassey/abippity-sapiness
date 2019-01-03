
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

