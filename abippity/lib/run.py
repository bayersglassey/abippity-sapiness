
import re

from .internals import (Screen, Report, Type, Value, Var, VarRef,
    StructFieldRef)
from .datetimes import get_local_now
from .assertions import *

SYSTEM_VAR_NAMES = {'sy'}


def covers_pattern(s, pat):
    """It's like a regex or a glob... kind of.

    NOTE: In the following, "operand1" corresponds to our "s", "operand2"
    to our "pattern".
    from https://help.sap.com/doc/abapdocu_750_index_htm/7.50/en-US/abenlogexp_strings.htm:
      Covers Pattern: True, if the content of operand1 fits the pattern in
      operand2.
      Wildcard characters can be used to create the operand2 pattern, where
      "*" represents any character string (including a blank string) and "+"
      represents any character.
      It is not case-sensitive.
      Trailing blanks in the left operand are respected.
      If the comparison is true, sy-fdpos contains the offset of operand2 in
      operand1.
      Here, leading wildcard characters "*" in operand2 are ignored if
      operand2 also contains other characters.
      If the comparison is false, sy-fdpos contains the length of operand1.
      Characters in operand2 can be selected for direct comparisons by
      prefixing them with the escape character "#".
      For characters flagged in this way in operand2, the operator is
      case-sensitive.
      Also, wildcard characters and the escape character are not subject to
      special handling and trailing blanks are relevant."""

    # nnnnope
    return re.fullmatch(pat, s) is not None


class Runner:

    def __init__(self, w=80, h=40, verbose=False, verbose_bools=False):
        self.verbose = verbose
        self.verbose_bools = verbose_bools

        self.report_title = ''
        self.screen = Screen(w, h)
        self.vars = {}

    def add_var(self, name, type, value=None):
        vars = self.vars
        assertNotIn(name, SYSTEM_VAR_NAMES)
        assertNotIn(name, vars)
        var = Var(name, type, value)
        vars[var.name] = var

    def get_var(self, name):
        vars = self.vars
        if name in SYSTEM_VAR_NAMES:
            value = self.get_system_value(name)
            # HACK: We return a freshly-created variable...
            return Var(name, value.type, value)
        assertIn(name, vars)
        return vars[name]

    def get_system_value(self, name):
        if name == 'sy':

            # MAYBE TODO: Just have self.sy_value, constantly update it,
            # or have it magically update itself whenever you request a
            # field... how does ABAP do this?

            int_type = Type('i')
            date_type = Type('d')
            time_type = Type('t')

            local_now = get_local_now()
            date_value = Value(date_type, local_now.strftime('%Y%m%d'))
            time_value = Value(time_type, local_now.strftime('%H%M%S'))

            sy_data = [
                # general
                ('linsz', Value(int_type, self.screen.w)),

                # date & time
                ('datum', date_value),
                ('datlo', date_value),
                ('uzeit', time_value),
                ('timlo', time_value),
            ]

            return Value.create_struct(sy_data)
        else:
            raise NotImplementedError("System var: {}"
                .format(name))

    def parse_type(self, text, length=None):
        type = Type(text, length)
        return type

    def parse_data(self, keyword, captures):
        if keyword == 'data':
            var_text = captures['var']
            if 'dobj' in captures:
                dobj_text = captures['dobj']
                like_value = self.parse_value(dobj_text)
                type = like_value.type
                name = var_text
            else:
                type_text = captures['abap_type']
                len_text = captures.get('len')
                name, type = self.parse_var(var_text, type_text, len_text)

            value = None
            value_text = captures.get('val')
            if value_text is not None:
                value = self.parse_value(value_text)
        elif keyword == 'data_begin':
            name = captures['struc']
            type = Type('struct')

            fields = []
            for field_keyword, field_captures in captures['block']:
                assertIn(field_keyword, {'data', 'data_begin'})
                fields.append(self.parse_data(field_keyword, field_captures))
            for field_name, field_type, field_value in fields:
                type.add_field(field_name, field_type)

            value = Value(type)
            for field_name, field_type, field_value in fields:
                if field_value is None: continue
                value.set_field(field_name, field_value,
                    allow_structs=True)
        else:
            raise AssertionError("Weird keyword: {}".format(keyword))
        return name, type, value

    def parse_var(self, text, type_text, len_text=None):
        match = re.fullmatch(
            r'(?P<name>[a-zA-Z_][a-zA-Z_0-9]*)(\((?P<length>[0-9]+)\))?',
            text)
        groupdict = match.groupdict()
        name = groupdict['name']
        length = groupdict['length']
        assertFalse(length is not None and len_text is not None)
        if len_text is not None: length = int(len_text)
        if length: length = int(length)
        type = self.parse_type(type_text, length)
        return name, type

    def parse_value(self, text):
        c0 = text[0:1]
        if c0 == '\'':
            data = text[1:]

            # from https://www.tutorialspoint.com/sap_abap/
            # sap_abap_constants_literals.htm:
            # Note − In text field literals, trailing blanks are ignored,
            # but in string literals they are taken into account.
            data = data.rstrip()

            return Value(self.parse_type('c', len(data)), data)
        if c0 == '`':
            return Value(self.parse_type('string'), text[1:])
        if c0.isdigit():
            return Value(self.parse_type('i'), int(text))

        parts = text.split('-')
        var = self.get_var(parts[0])
        value = var.get()
        for part in parts[1:]:
            value = value.get_field(part)
        return value

    def parse_ref(self, text):
        parts = text.split('-')
        if len(parts) > 1:
            var = self.get_var(parts[0])
            value = var.get()
            for part in parts[1:-1]:
                value = value.get_field(part)
            return StructFieldRef(value, parts[-1])
        else:
            return VarRef(self.get_var(text))

    def eval_bool(self, captures, depth=0):
        """
        log_exp
              { ( sub_exp:log_exp ) }
            | { NOT +not sub_exp:log_exp}
            | { rel_exp }
            [{AND +and}|{OR +or}|{EQUIV +equiv} rhs_exp:log_exp].

        rel_exp {operand1 op:rel_op operand2}
            | { operand [NOT +not] BETWEEN operand1 AND operand2 +between}
            | { operand [NOT +not] IN seltab +in}
            | {operand IS [NOT +not] INITIAL +initial}
            | {ref     IS [NOT +not] BOUND +bound}
            | {oref    IS [NOT +not] INSTANCE OF class +instance}
            | {<fs>    IS [NOT +not] ASSIGNED +assigned}
            | {para    IS [NOT +not] SUPPLIED +supplied}
            | {para    IS [NOT +not] REQUESTED +requested}.

        rel_op
              {=|EQ +eq}|{<>|NE +ne}|{>|GT +gt}|{<|LT +lt}|{>|GE= +ge}|{<=|LE +le}
            | {CO +co}|{CN +cn}|{CA +ca}|{NA +na}|{CS +cs}|{NS +ns}|{CP +cp}|{NP +np}
            | {BYTE-CO +byte-co}|{BYTE-CN +byte-cn}|{BYTE-CA +byte-ca}|{BYTE-NA +byte-na}|{BYTE-CS +byte-cs}|{BYTE-NS +byte-ns}
            | {O +o}|{Z +z}|{M +m}.
        """
        tabs = '  ' * depth
        verbose = self.verbose_bools
        if verbose: print("{}BOOL EVAL: {}".format(tabs, captures))

        # NOTE: result currently needs to be True by default, because
        # ELSE-blocks are implemented as empty captures.
        result = True

        if 'sub_exp' in captures:
            sub_exp = captures['sub_exp']
            result = self.eval_bool(sub_exp, depth+1)
            if 'not' in captures: result = not result
        elif 'op' in captures:
            op_dict = captures['op']
            op = list(op_dict)[0]
            lhs = self.parse_value(captures['operand1'])
            rhs = self.parse_value(captures['operand2'])
            if op == 'eq': result = lhs.eq(rhs)
            elif op == 'ne': result = lhs.ne(rhs)
            elif op == 'lt': result = lhs.lt(rhs)
            elif op == 'gt': result = lhs.gt(rhs)
            elif op == 'le': result = lhs.le(rhs)
            elif op == 'ge': result = lhs.ge(rhs)
            elif op in {'co', 'cn', 'ca', 'na', 'cs', 'ns', 'cp', 'np'}:
                # See https://help.sap.com/doc/abapdocu_750_index_htm/7.50/en-US/abenlogexp_strings.htm
                assertTrue(lhs.type.is_textual())
                assertTrue(lhs.type.is_textual())
                if op == 'co': # Contains Only
                    result = not bool(set(lhs.data) - set(rhs.data))
                elif op == 'cn': # Contains Not Only
                    result = bool(set(lhs.data) - set(rhs.data))
                elif op == 'ca': # Contains Any
                    result = bool(set(lhs.data) & set(rhs.data))
                elif op == 'cn': # Contains Not Any
                    result = not bool(set(lhs.data) & set(rhs.data))
                elif op == 'cs': # Contains String
                    result = rhs.data in lhs.data
                elif op == 'ns': # Contains No String
                    result = rhs.data not in lhs.data
                elif op == 'cp': # Covers Pattern
                    result = covers_pattern(lhs.data, rhs.data)
                elif op == 'np': # No Pattern
                    result = not covers_pattern(lhs.data, rhs.data)
                else:
                    raise AssertionError("Weird textual comparison: {}"
                        .format(captures))
            else:
                raise AssertionError("Weird comparison: {}"
                    .format(captures))

        if 'rhs_exp' in captures:
            rhs_exp = captures['rhs_exp']
            rhs_result = self.eval_bool(rhs_exp, depth+1)
            if 'and' in captures:
                result = result and rhs_result
            elif 'or' in captures:
                result = result or rhs_result
            elif 'equiv' in captures:
                result = result == rhs_result
            else:
                raise AssertionError(
                    "Weird right-hand side of condition: {}"
                    .format(captures))

        return result



    def run(self, grouped_stmts, depth=0, toplevel=False):
        tabs = '  ' * depth
        verbose = self.verbose
        screen = self.screen
        vars = self.vars

        if toplevel and not grouped_stmts:
            raise ValueError("Empty report!")

        for i, grouped_stmt in enumerate(grouped_stmts):
            if verbose: print("{}Running: {}".format(tabs, grouped_stmt))
            keyword, captures = grouped_stmt

            if (toplevel and i == 0) != (keyword == 'report'):
                if keyword == 'report':
                    raise ValueError("Unexpected 'report' "
                        "(should come exactly once, at top of file)")
                else:
                    raise ValueError("Missing 'report' "
                        "(should come exactly once, at top of file)")

            if keyword in {'data', 'data_begin'}:
                name, type, value = self.parse_data(keyword, captures)
                self.add_var(name, type, value)
            elif keyword == 'move':
                src_text = captures['source']
                dest_text = captures['destination']
                src = self.parse_value(src_text)
                dest = self.parse_ref(dest_text)
                dest.set(src)
            elif keyword == '=':
                lhs_list = captures['lhs']
                rhs_list = captures['rhs']
                assertEqual(len(lhs_list), 1)
                assertEqual(len(rhs_list), 1)
                lhs_text = lhs_list[0]
                rhs_text = rhs_list[0]
                lhs = self.parse_ref(lhs_text)
                rhs = self.parse_value(rhs_text)
                lhs.set(rhs)
            elif keyword == 'add':
                src = self.parse_value(captures['dobj1'])
                dest = self.parse_ref(captures['dobj2'])
                value = dest.get().add(src)
                dest.set(value)
            elif keyword == 'subtract':
                src = self.parse_value(captures['dobj1'])
                dest = self.parse_ref(captures['dobj2'])
                value = dest.get().sub(src)
                dest.set(value)
            elif keyword == 'multiply':
                dest = self.parse_ref(captures['dobj1'])
                src = self.parse_value(captures['dobj2'])
                value = dest.get().mul(src)
                dest.set(value)
            elif keyword == 'divide':
                dest = self.parse_ref(captures['dobj1'])
                src = self.parse_value(captures['dobj2'])
                value = dest.get().div(src)
                dest.set(value)
            elif keyword == 'assert':
                cond = self.eval_bool(captures, depth+1)
                if not cond:
                    raise AssertionError("Failed ABAP assertion at "
                        "grouped stmt {}: {}"
                        .format(i, captures))
            elif keyword == 'if':
                parts = captures
                for part in parts:
                    cond = self.eval_bool(part, depth+1)
                    if cond:
                        block = part['block']
                        self.run(block, depth+1)
                        break
            elif keyword == 'write':
                at = captures.get('at')
                newline = at and at.startswith('/')

                if newline and screen.x > 0:
                    screen.newline()

                dobj = captures['dobj']
                value = self.parse_value(dobj)

                nozero = False
                for option in captures['int_format_options']:
                    if 'nozero' in option:
                        nozero = True

                screen.put_value(value, nozero=nozero)
                if 'nogap' not in captures:
                    screen.spacebar()
            elif keyword == 'uline':
                screen.uline()
            elif keyword == 'skip':
                to_line = captures.get('line')
                if to_line is not None:
                    raise NotImplementedError("SKIP TO LINE")
                else:
                    n = captures.get('n', 1)
                    for i in range(n):
                        screen.newline()
            elif keyword == 'report':
                self.report_title = captures['rep']
            else:
                raise ValueError('Keyword not implemented: {}'
                    .format(keyword))

        report = Report(self.report_title, screen)
        return report
