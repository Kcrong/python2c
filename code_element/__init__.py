from .defines import *


class Start:
    # C에서 중괄호 열림 표현을 위해 만든 클래스
    def __init__(self):
        self.__string = "{"

    def __str__(self):
        return self.__string


class Finish:
    # C에서 중괄호 닫힘 표현을 위해 만든 클래스

    def __init__(self):
        self.__string = "}"

    def __str__(self):
        return self.__string


TYPE_DEF = {
    int: 'int',
    str: 'char',
}
"""
대괄호(square bracket) : []
중괄호(brace) : {}
소괄호 (parenthesis): ()
"""

OPEN_BRACE = Start()
CLOSE_BRACE = Finish()

AVOID_SEMICOLON = [OPEN_BRACE, CLOSE_BRACE]


class Var:
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.__type = None

    def __repr__(self):
        return "<Var %s>" % self.name

    @staticmethod
    def find_type_class(value):
        try:
            return {
                int: Integer,
                str: Char
            }[type(value)]
        except KeyError:
            print("Not Support Type!!")
            raise


class Integer(Var):
    def __init__(self, name, data):
        super().__init__(name, data)
        self.__type = 'int'

    def __repr__(self):
        return "<Integer %s>" % self.name

    def __str__(self):
        return "%s %s = %s" % (self.__type, self.name, self.data)


class Char(Var):
    def __init__(self, name, data):
        super().__init__(name, data)
        self.data_len = len(self.data) + 1
        self.__type = 'char'

    def __str__(self):
        if self.data_len == 1:
            return "%s %s = '%s'" % (self.__type, self.name, self.data)
        else:
            return "%s %s[%d] = \"%s\"" % (self.__type, self.name, self.data_len, self.data)


class Include:
    def __init__(self, name):
        self.name = name
        self.__string = "#include <%s>" % self.name

    def __repr__(self):
        return "<Include %s>" % self.name

    def __str__(self):
        return self.__string


class Function:
    def __init__(self, name, rtn_type, argv=None):
        self.argv = argv
        self.name = name
        self.__code = list()
        self.var = list()
        self.type = rtn_type

    def __make_string(self):
        all_code = "%s %s(" % (self.type, self.name)

        if self.argv is not None:
            for argv in self.argv:
                all_code += "%s %s," % (argv.type, argv.name)

        all_code += ")"

        all_code += str(OPEN_BRACE)
        all_code += NEXT_LINE

        for var in self.var:
            all_code += str(var)
            all_code += (SEMICOLON + NEXT_LINE)

        for code in self.__code:
            all_code += str(code)
            if code not in AVOID_SEMICOLON:
                all_code += SEMICOLON
            all_code += NEXT_LINE

        all_code += NEXT_LINE
        all_code += str(CLOSE_BRACE)

        return all_code

    def add_var(self, var_obj):
        self.var.append(var_obj)

    def add_code(self, code_obj):
        self.__code.insert(-1, code_obj)

    def find_var(self, var_name):
        for var in self.var:
            if var.name == var_name:
                return var
        else:
            return None

    def __repr__(self):
        return "<Func %s>" % self.name

    def __str__(self):
        return self.__make_string()
