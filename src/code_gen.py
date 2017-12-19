from lark import Transformer
from collections import namedtuple
import textwrap

Expression = namedtuple('Expression', ['type_name', 'go_code'])
Variable = namedtuple('Variable', ['ol_name', 'go_name', 'type_name'])


def snake_to_camel(name):
    words = name.split("_")
    if len(words) > 1:
        camel_name = words[0] + "".join(map(str.capitalize, words[1:]))
    else:
        camel_name = words[0]
    return camel_name


class SymbolTable:
    def __init__(self):
        self.table = {}

    def set(self, name, variable):
        self.table[name] = variable

    def get(self, name):
        return self.table[name]


class CodeGen(Transformer):
    def __init__(self):
        self.symbol_table = SymbolTable()

    def program(self, args):
        lines = "\n".join(args)
        go_body = textwrap.dedent("""
            package main
            
            func main() {{
            {lines}
            }}
            
            """)
        return go_body.format(lines=textwrap.indent(lines, "\t"))

    def decl(self, args):
        name, expr = args
        go_name = snake_to_camel(name)
        self.symbol_table.set(name, Variable(name, go_name, expr.type_name))
        return f"{go_name} := {expr.go_code}"

    def var_decl(self, args):
        return args[0]

    def var_usage(self, args):
        return args[0]

    def int(self, args):
        return Expression(type_name="int", go_code=args[0])

    def float(self, args):
        return Expression(type_name="float64", go_code=args[0])

    def bool(self, args):
        return Expression(type_name="bool", go_code=args[0])

    def string(self, args):
        return Expression(type_name="string", go_code=args[0])

    def list(self, args):
        item_type = args[0].type_name
        type_name = f"[]{item_type}"
        arg_code = [arg.go_code for arg in args]
        arg_code = ", ".join(arg_code)
        go_code = f"{type_name}{{{arg_code}}}"
        return Expression(type_name, go_code)

    def type_def(self, args):
        name, defn = args
        go_code = f"""
        type {name} struct {{
        
        }}
        
        """
