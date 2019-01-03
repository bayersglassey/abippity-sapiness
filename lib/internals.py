
from .utils import assertIn, assertEqual, assertGreaterEqual



BASETYPES = {'x', 'c', 'n', 'd', 't', 'i', 'f', 'p', 'string', 'xstring'}
FIXED_LENGTH_BASETYPES = {'x', 'c', 'n', 'p'}
DEFAULT_BASETYPE_LENGTHS = {'c': 1, 'n': 1}
FORCED_BASETYPE_LENGTHS = {'d': 8, 't': 6}
DYNAMIC_LENGTH_BASETYPES = {'string', 'xstring'}
NUMERIC_BASETYPES = {'n', 'i', 'f', 'p'}
TEXTUAL_BASETYPES = {'c', 'string', 'xstring'}
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
    def uline(self):
        if self.x != 0:
            self.newline()
        for i in range(self.w):
            self.putc('-')
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
        assertEqual(length is not None, basetype in FIXED_LENGTH_BASETYPES)
        if basetype in FORCED_BASETYPE_LENGTHS:
            length = FORCED_BASETYPE_LENGTHS[basetype]
        self.basetype = basetype
        self.length = length
    def __str__(self):
        return "{}".format(self.basetype)
    def __repr__(self):
        return "Type({})".format(self)
    def convert(self, value):

        # WARNING: This method needs a loooot of work.
        # See: https://help.sap.com/doc/abapdocu_752_index_htm/7.52/en-US/abenconversion_rules.htm
        # See also: https://www.tutorialspoint.com/sap_abap/sap_abap_operators.htm:
        #     Following is the order of preference −
        #     If one field is of type I, then the other is converted to type I.
        #     If one field is of type P, then the other is converted to type P.
        #     If one field is of type D, then the other is converted to type D. But C and N types are not converted and they are compared directly. Similar is the case with type T.
        #     If one field is of type N and the other is of type C or X, both the fields are converted to type P.
        #     If one field is of type C and the other is of type X, the X type is converted to type C.

        self_basetype = self.basetype
        value_type = value.type
        value_basetype = value_type.basetype

        if self.length is not None:
            assertGreaterEqual(self.length, value.get_length())

        if self.is_numeric() and value_type.is_numeric():
            return Value(self, value.data)

        if self.is_textual() and value_type.is_textual():
            return Value(self, value.data)

        assertEqual(self_basetype, value_basetype)
        return value

    def is_numeric(self):
        return self.basetype in NUMERIC_BASETYPES
    def is_textual(self):
        return self.basetype in TEXTUAL_BASETYPES
    def get_initial(self):
        """Returns the \"initial\" value for the given ABAP type
        (that is, the value for which the ABAP expression
        \"<value> IS INITIAL\" is true)"""
        basetype = self.basetype
        if self.is_numeric():
            return Value(self, 0)
        elif self.is_textual():
            return Value(self, "")
        else:
            raise ValueError("Not implemented for type: {}"
                .format(self))

class Value:
    def __init__(self, type, data):
        self.type = type
        self.data = data
    def __str__(self):
        return "{}".format(repr(self.data))
    def __repr__(self):
        return "Value({} TYPE {})".format(repr(self.data), self.type)
    def get_length(self):
        type = self.type
        if type.length is not None:
            return type.length
        if type.is_numeric():
            return len(str(self.data))
        if type.is_textual():
            return len(self.data)
        raise NotImplemented()
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

