
from .utils import assertIn, assertEqual



BASETYPES = {'x', 'c', 'n', 'd', 't', 'i', 'f', 'p', 'string', 'xstring'}
FIXEDLENGTH_BASETYPES = {'x', 'c', 'n', 'p'}
DEFAULT_BASETYPE_LENGTHS = {'c': 1, 'n': 1}
DYNAMICLENGTH_BASETYPES = {'string', 'xstring'}
NUMERIC_BASETYPES = {'n', 'i', 'f', 'p'}
"""
from https://wiki.scn.sap.com/wiki/display/ABAP/ABAP+Types:
Elementary Types supported by ABAP
    Fixed length:
        characters (C)
        numbers: numeric text (N), integers (I), packed (P), floating decimal point (F)
        Date (D)
        Time (T)
        Hexadecimal (X)
    Variable length:
        String
        Xstring
"""


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
    def put_value(self, value, **kwargs):
        self.puts(value.to_text(**kwargs))
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
    def __init__(self, basetype, length=None):
        assertIn(basetype, BASETYPES)
        if length is None:
            length = DEFAULT_BASETYPE_LENGTHS.get(basetype)
        assertEqual(length is not None, basetype in FIXEDLENGTH_BASETYPES)
        self.basetype = basetype
        self.length = length
    def __str__(self):
        return "{}".format(self.basetype)
    def __repr__(self):
        return "Type({})".format(self)
    def convert(self, value):

        # WARNING: This method needs a loooot of work.
        # See: https://help.sap.com/doc/abapdocu_752_index_htm/7.52/en-US/abenconversion_rules.htm

        self_basetype = self.basetype
        value_type = value.type
        value_basetype = value_type.basetype

        if self_basetype == 'n':
            if value_basetype == 'i':
                return Value(self, value.data)

        assertEqual(self_basetype, value_basetype)
        if self.length is not None:
            assertEqual(self.length, value_type.length)
        return value

    def is_numeric(self):
        return self.basetype in NUMERIC_BASETYPES
    def get_initial(self):
        """Returns the \"initial\" value for the given ABAP type
        (that is, the value for which the ABAP expression
        \"<value> IS INITIAL\" is true)"""
        basetype = self.basetype
        if basetype == 'i':
            return Value(self, 0)
        elif basetype == 'n':
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
    def to_text(self, nozero=False):
        s = str(self.data)
        type = self.type
        if type.is_numeric():
            length = type.length
            if length is not None and not nozero:
                s = s.rjust(length, '0')
        return s

class Var:
    def __init__(self, name, type, value=None):
        self.name = name.lower()
        self.type = type
        if value is None:
            value = type.get_initial()
        self.set(value)
    def __str__(self):
        s = "{}".format(self.name)
        length = self.type.length
        if length is not None:
            s = "{}({})".format(s, length)
        return "{} TYPE {} VALUE {}".format(s, self.type, self.value)
    def __repr__(self):
        return "Var({})".format(self)
    def get(self):
        return self.value
    def set(self, value):
        value = self.type.convert(value)
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

