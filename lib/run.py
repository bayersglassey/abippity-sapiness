
import re

from .internals import Screen, Report, Type, Value, Var, Ref


class Runner:

    def __init__(self, w=80, h=40, verbose=False):
        self.verbose = verbose

        self.report_title = ''
        self.screen = Screen(w, h)
        self.vars = {}

    def parse_type(self, text, length=None):
        type = Type(text, length)
        return type

    def parse_var(self, text, type_text):
        match = re.fullmatch(
            r'(?P<name>[a-zA-Z_][a-zA-Z_0-9]*)(\((?P<length>[0-9]+)\))?',
            text)
        groupdict = match.groupdict()
        name = groupdict['name']
        length = groupdict['length']
        if length: length = int(length)
        type = self.parse_type(type_text, length)
        return Var(name, type)

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
        return self.vars[text].get()

    def parse_ref(self, text):
        return Ref(self.vars[text])



    def run(self, parsed_stmts):
        verbose = self.verbose
        screen = self.screen
        vars = self.vars

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
                var = self.parse_var(var_text, type_text)
                vars[var.name] = var
            elif keyword == 'move':
                src_text = captures['source']
                dest_text = captures['destination']
                src = self.parse_value(src_text)
                dest = self.parse_ref(dest_text)
                dest.set(src)
            elif keyword == 'write':
                if 'newline' in captures:
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
                    raise NotImplemented("SKIP TO LINE")
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
