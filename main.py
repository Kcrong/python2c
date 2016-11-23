import ast
import sys

from code_element import *
from code_element.defines import *

write = sys.stdout.write


class SourceCode:
    def __init__(self):
        self.include = list()
        self.func = dict()
        self.func_key = list()
        self.init_code()

    def init_code(self):
        self.add_include(Include(DEFAULT_INCLUDE_MODULE))
        self.add_func(Function(START_FUNC_NAME, TYPE_DEF[int]))

    def add_include(self, module_obj):
        self.include.append(module_obj)

    def add_func(self, func_obj):
        self.func[func_obj.name] = func_obj
        self.func_key.append(func_obj.name)

    def include2code(self):
        code = ""
        for include in self.include:
            code += str(include)

        code += (NEXT_LINE + NEXT_LINE)

        return code

    @property
    def code(self):
        return self.__make_code()

    def __make_code(self):
        all_code = ""

        all_code += self.include2code()

        for func_name in self.func_key:
            func = self.func[func_name]
            all_code += str(func)

        return all_code


class Converter:
    def __init__(self, module_name):
        self.modulename = module_name
        self.source_code = SourceCode()
        self.output_name = module_name + ".c"
        self.input_source_code = self.__get_input_source()
        self.processing_func = None

    def __get_input_source(self):
        with open(self.modulename + '.py', 'r') as f:
            return list(map(lambda s: s.strip(), f.readlines()))

    def __write_file(self):
        with open(self.output_name, 'w') as f:
            f.write(self.source_code.code)

    def get_func_by_name(self, func_name):
        return self.source_code.func[func_name]

    # c_func_processor
    def make_printf_string(self, body):
        args = body.args
        raise RuntimeError("개발중입니다!")

    def call_func_mapper(self, body):
        """
        C와 Python 함수 매퍼
        """
        c_func_processor = {
            'print': self.make_printf_string
        }[body.func.id]

        c_func_processor(body)

    def get_body_value(self, body):
        try:
            value_class = body.value.__class__
        except AttributeError:
            value_class = body.__class__

        return {
            ast.Str: (lambda x: x.s),
            ast.Num: (lambda x: x.n),
            ast.Name: (lambda x: self.processing_func.find_var(x.id).data),
            ast.BinOp: self.code_value,
            ast.Call: (lambda x: self.call_func_mapper(x))
        }[value_class](body)

    def get_body_string(self, body):
        if body.__class__ != ast.Name:
            return self.get_body_value(body)
        else:
            return self.processing_func.find_var(body.id).name

    @staticmethod
    def get_op_string(op_class):
        return {
            ast.Add: '+',
            ast.Sub: '-',
            ast.Div: '/',
            ast.Mult: '*'
        }[op_class.__class__]

    # For expr code
    def code_value(self, bin_op_obj):
        left_value = self.get_body_value(bin_op_obj.left)
        right_value = self.get_body_value(bin_op_obj.right)
        op_string = self.get_op_string(bin_op_obj.op)
        return eval("%s %s %s" % (left_value, op_string, right_value))

    # For expr code
    def code_string(self, bin_op_obj):
        if bin_op_obj.__class__ != ast.BinOp:
            return self.get_body_value(bin_op_obj)
        left_value = self.get_body_string(bin_op_obj.left)
        right_value = self.get_body_string(bin_op_obj.right)
        op_string = self.get_op_string(bin_op_obj.op)
        return "%s %s %s" % (left_value, op_string, right_value)

    def expr_code(self, body):
        self.processing_func.add_code(self.code_string(body.value))

    def assign_code(self, body):
        value_string = self.code_string(body.value)
        value = self.get_body_value(body.value)
        for target in body.targets:
            type_class = Var.find_type_class(value)
            self.processing_func.add_var(type_class(target.id, value_string))

    def aug_assign_code(self, body):
        var = self.processing_func.find_var(body.target.id)
        op_string = Converter.get_op_string(body.op)
        right_string = "%s %s %s" % (var.name, op_string, self.code_string(body.value))

        code = "%s = %s" % (var.name, right_string)
        self.processing_func.add_code(code)

    def convert(self):
        code_type = {
            ast.Assign: self.assign_code,
            ast.Expr: self.expr_code,
            ast.AugAssign: self.aug_assign_code,
        }
        for func_name in self.source_code.func_key:
            self.processing_func = self.get_func_by_name(func_name)
            for source in self.input_source_code:
                parse = ast.parse(source)
                for body in parse.body:
                    code_type[body.__class__](body)

        self.__write_file()


if __name__ == '__main__':
    c = Converter(sys.argv[1])
    c.convert()
