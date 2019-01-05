
from collections import OrderedDict

from .assertions import *



BASETYPES = {'x', 'c', 'n', 'd', 't', 'i', 'f', 'p',
    'string', 'xstring', 'struct'}
FIXED_LENGTH_BASETYPES = {'x', 'c', 'n', 'p'}
DEFAULT_BASETYPE_LENGTHS = {'c': 1, 'n': 1}
FORCED_BASETYPE_LENGTHS = {'d': 8, 't': 6}
DYNAMIC_LENGTH_BASETYPES = {'string', 'xstring'}
NUMERIC_BASETYPES = {'n', 'i', 'f', 'p'}
TEXTUAL_BASETYPES = {'c', 'd', 't', 'string', 'xstring'}
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

See also, conversion charts for all elementary types:
https://help.sap.com/doc/saphelp_470/4.7/en-US/fc/eb3434358411d1829f0000e829fbfe/content.htm:
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
    def print(self, file=None):
        print("REPORT: {}".format(self.title.upper()), file=file)
        screen = self.screen
        uline = '*' * screen.w
        print(uline, file=file)
        for line in screen.as_lines():
            print(line, file=file)
        print(uline, file=file)


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
        if self.is_struct():
            self.fields = OrderedDict()
    def __str__(self):
        if self.is_struct():
            return "BEGIN {} END".format(
                ' '.join("{} TYPE {},".format(name, type)
                    for name, type in self.fields.items()))
        return "{}".format(self.basetype)
    def __repr__(self):
        return "Type({})".format(self)
    @classmethod
    def numeric_lcd(Type, type1, type2):
        # WARNING: This is just plain wrong... but our numeric types basically all behave the same, so whatever.
        # See https://help.sap.com/doc/saphelp_470/4.7/en-US/fc/eb3434358411d1829f0000e829fbfe/content.htm
        assertTrue(type1.is_numeric())
        assertTrue(type2.is_numeric())
        return type1
    def convert(self, value, allow_structs=False):

        # WARNING: This method needs a loooot of work.
        # See: https://help.sap.com/doc/abapdocu_752_index_htm/7.52/en-US/abenconversion_rules.htm
        # See also: https://www.tutorialspoint.com/sap_abap/sap_abap_operators.htm:
        #     Following is the order of preference −
        #     If one field is of type I, then the other is converted to type I.
        #     If one field is of type P, then the other is converted to type P.
        #     If one field is of type D, then the other is converted to type D. But C and N types are not converted and they are compared directly. Similar is the case with type T.
        #     If one field is of type N and the other is of type C or X, both the fields are converted to type P.
        #     If one field is of type C and the other is of type X, the X type is converted to type C.

        if not allow_structs:
            if self.is_struct():
                raise AssertionError("Struct conversion not allowed: "
                    "{} to {}"
                    .format(repr(value), repr(self)))

        if self.length is not None:
            assertGreaterEqual(self.length, value.get_length())

        if self.is_numeric() and value.is_numeric():
            return Value(self, value.data)

        if self.is_textual() and value.is_textual():
            return Value(self, value.data)

        assertEqual(self.basetype, value.type.basetype)
        return value

    def is_struct(self):
        return self.basetype == 'struct'
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

    def add_field(self, name, type):
        assertTrue(self.is_struct())
        assertNotIn(name, self.fields)
        self.fields[name] = type


class Value:
    def __init__(self, type, data=None):
        self.type = type
        if type.is_struct():
            self.fields = OrderedDict(
                (name, Value(subtype))
                for name, subtype in type.fields.items())
        else:
            if data is None: data = type.get_initial()
            self.data = data
    def __str__(self):
        if self.is_struct():
            return "BEGIN {} END".format(
                ' '.join("{} = {},".format(name, value)
                    for name, value in self.fields.items()))
        return "{}".format(repr(self.data))
    def __repr__(self):
        if self.is_struct():
            return "Value(BEGIN {} END)".format(
                ', '.join("{} = {}".format(name, value)
                for name, value in self.fields.items()))
        return "Value({} TYPE {})".format(repr(self.data), self.type)
    @classmethod
    def create_struct(Value, items):
        type = Type('struct')
        for name, value in items:
            type.add_field(name, value.type)
        struct_value = Value(type)
        for name, value in items:
            struct_value.set_field(name, value)
        return struct_value
    def is_numeric(self): return self.type.is_numeric()
    def is_textual(self): return self.type.is_textual()
    def is_struct(self): return self.type.is_struct()
    def get_length(self):
        type = self.type
        if type.length is not None:
            return type.length
        if type.is_numeric():
            return len(str(self.data))
        if type.is_textual():
            return len(self.data)
        raise NotImplementedError()
    def eq(self, other):
        return self.data == other.data
    def ne(self, other):
        return self.data != other.data
    def lt(self, other):
        return self.data < other.data
    def gt(self, other):
        return self.data > other.data
    def le(self, other):
        return self.data <= other.data
    def ge(self, other):
        return self.data >= other.data
    def add(self, other):
        type = Type.numeric_lcd(self.type, other.type)
        return Value(type, self.data + other.data)
    def sub(self, other):
        type = Type.numeric_lcd(self.type, other.type)
        return Value(type, self.data - other.data)
    def mul(self, other):
        type = Type.numeric_lcd(self.type, other.type)
        return Value(type, self.data * other.data)
    def div(self, other):
        type = Type.numeric_lcd(self.type, other.type)
        return Value(type, self.data // other.data)
    def to_text(self, nozero=False):
        s = str(self.data)
        type = self.type
        if type.is_numeric():
            length = type.length
            if length is not None and not nozero:
                s = s.rjust(length, '0')
        return s
    def get_field(self, name):
        assertTrue(self.is_struct())
        assertIn(name, self.fields)
        return self.fields[name]
    def set_field(self, name, value, allow_structs=False):
        assertTrue(self.is_struct())
        assertIn(name, self.fields)
        value = self.type.fields[name].convert(value,
            allow_structs=allow_structs)
        self.fields[name] = value

class Var:
    def __init__(self, name, type, value=None):
        self.name = name.lower()
        self.type = type
        if value is None: value = Value(type)
        self.set(value, allow_structs=True)
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
    def set(self, value, allow_structs=False):
        value = self.type.convert(value,
            allow_structs=allow_structs)
        self.value = value

class Ref:
    def __init__(self):
        raise NotImplementedError("Don't use Ref directly, use its subclasses!")
    def __repr__(self):
        return "Ref({})".format(self)

class VarRef:
    def __init__(self, var):
        self.var = var
    def __str__(self):
        return "REF TO {}".format(self.var)
    def get(self):
        return self.var.get()
    def set(self, value):
        self.var.set(value)

class StructFieldRef:
    def __init__(self, struct, field_name):
        self.struct = struct
        self.field_name = field_name
    def __str__(self):
        return "REF TO FIELD {} OF {}".format(self.field_name, self.struct)
    def get(self):
        return self.struct.get_field(self.field_name)
    def set(self, value):
        self.struct.set_field(self.field_name, value)

