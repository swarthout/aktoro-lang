from lark import Transformer
from collections import namedtuple
import textwrap

Expression = namedtuple('Expression', ['type_name', 'go_code'])
Variable = namedtuple('Variable', ['name', 'type_name'])
Record = namedtuple('Record', ['name', 'fields'])


def snake_to_camel(name):
    words = name.split("_")
    if len(words) > 1:
        camel_name = words[0] + "".join(map(str.capitalize, words[1:]))
    else:
        camel_name = words[0]
    return camel_name


class SymbolTable:
    def __init__(self):
        self.table = [{}]

    def add_symbol(self, name, data):
        self.table[-1][name] = data

    def get_symbol(self, name):
        for scope in reversed(self.table):
            if name in scope.keys():
                return scope[name]
        raise KeyError(name)

    def push_scope(self):
        self.table.append({})

    def pop_scope(self):
        self.table.pop()


class RecordTable:
    def __init__(self):
        self.table = {}
        self.name_table = {}

    @staticmethod
    def hash_field_names(field_names):
        fields_sorted = sorted(field_names)
        field_hash = "#".join(fields_sorted)
        return field_hash

    def get_record_by_name(self, name):
        field_hash = self.name_table[name]
        return self.table[field_hash]

    def get_by_field_names(self, field_names):
        field_hash = self.hash_field_names(field_names)
        return self.table[field_hash]

    def insert_record(self, record):
        field_names = list(record.fields.keys())
        field_hash = self.hash_field_names(field_names)
        self.name_table[record.name] = field_hash
        self.table[field_hash] = record


class CodeGen(Transformer):
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.record_table = RecordTable()
        self.imports = []

    def program(self, args):
        lines = "\n".join(args)
        import_go_code = ""
        if self.imports:
            import_tmpl = textwrap.dedent("""
            import (
            {imports}
            )
            """)
            import_names = "\n".join(self.imports)
            import_go_code = import_tmpl.format(imports=textwrap.indent(import_names, "\t"))

        go_body = textwrap.dedent("""
            package main
            {imports}
            
            func main() {{
            {lines}
            }}
            
            """)
        return go_body.format(lines=textwrap.indent(lines, "\t"), imports=import_go_code)

    def decl(self, args):
        name, expr = args
        self.symbol_table.add_symbol(name, Variable(name, expr.type_name))
        return f"{name} := {expr.go_code}"

    def var_decl(self, args):
        return snake_to_camel(args[0])

    def var_usage(self, args):
        root_name = snake_to_camel(args[0])
        root_var = self.symbol_table.get_symbol(root_name)
        var_type = root_var.type_name
        if len(args) > 1:
            for arg in args[1:]:
                arg_name = snake_to_camel(arg)
                record = self.record_table.get_record_by_name(var_type)
                var_type = record.fields[arg_name]

        full_name = ".".join([snake_to_camel(name) for name in args])
        return Expression(type_name=var_type, go_code=full_name)

    def int_literal(self, args):
        return Expression(type_name="int", go_code=args[0])

    def float_literal(self, args):
        return Expression(type_name="float64", go_code=args[0])

    def bool_literal(self, args):
        return Expression(type_name="bool", go_code=args[0])

    def string_literal(self, args):
        return Expression(type_name="string", go_code=args[0])

    def list_literal(self, args):
        item_type = args[0].type_name
        type_name = f"[]{item_type}"
        arg_code = [arg.go_code for arg in args]
        arg_code = ", ".join(arg_code)
        go_code = f"{type_name}{{{arg_code}}}"
        return Expression(type_name, go_code)

    def add_expr(self, args):
        left, right = args
        go_code = f"{left.go_code} + {right.go_code}"
        return Expression(left.type_name, go_code)

    def type_def(self, args):
        name, field_defs = args
        r = Record(name=name, fields={})
        for f in field_defs:
            r.fields[f["name"]] = f["type_name"]
        self.symbol_table.add_symbol(name, r)
        self.record_table.insert_record(r)
        field_go_code = [f["go_code"] for f in field_defs]
        field_go_code = textwrap.indent("\n".join(field_go_code), "\t")
        go_code = textwrap.dedent("""
        type {name} struct {{
        {fields}
        }}
        """)
        return go_code.format(name=name, fields=field_go_code)

    def record_def(self, args):
        return args[0]

    def type_decl(self, args):
        return snake_to_camel(args[0])

    def param_list(self, args):
        return args

    def param(self, args):
        name, type_name = args
        self.symbol_table.add_symbol(name, Variable(name, type_name))
        return {
            "name": name,
            "type_name": type_name,
            "go_code": f"{name} {type_name}"
        }

    def type_usage(self, args):
        return snake_to_camel(args[0])

    def record_literal(self, args):
        field_names = [field["name"] for field in args]
        record = self.record_table.get_by_field_names(field_names)
        fields_go_code = ",\n".join([field["go_code"] for field in args])
        go_code = f"{record.name}{{\n" + textwrap.indent(fields_go_code, "\t") + textwrap.dedent("}")
        return Expression(type_name=record.name, go_code=go_code)

    def field_assignment(self, args):
        name, expr = args
        return {
            "name": name,
            "expr": expr,
            "go_code": f"{name}: {expr.go_code}"
        }

    def field_decl(self, args):
        name, type_name = args
        name = snake_to_camel(name)
        return {
            "name": name,
            "type_name": type_name,
            "go_code": f"{name} {type_name}"
        }

    def field_list(self, args):
        return args

    def field_name(self, args):
        return snake_to_camel(args[0])

    def func_def(self, args):
        _, params, _, return_type, func_body = args
        param_types = [param["type_name"] for param in params]
        param_types = ", ".join(param_types)
        func_type = f"func({param_types}) {return_type}"
        params = [param["go_code"] for param in params]
        params = ", ".join(params)
        func_body = "\n".join(line.go_code for line in func_body)
        go_code = """func ({params}) {return_type} {{
        {func_body}
        }}
        """
        go_code = go_code.format(params=params, return_type=return_type, func_body=func_body)
        return Expression(type_name=func_type, go_code=go_code)

    def func_body(self, args):
        args.pop(0)  # remove open block instruction
        args.pop()  # remove close block instruction
        last_expr = args[-1]
        last_expr = self.return_expr(last_expr)
        args[-1] = last_expr
        return args

    def func_call(self, args):
        func_type = args[0].type_name
        expr_type = func_type.rsplit(")", 1)[-1]
        arg_code = [arg.go_code for arg in args[1:]]
        arg_code = ",".join(arg_code)
        go_code = f"{args[0].go_code}({arg_code})"
        return Expression(type_name=expr_type, go_code=go_code)

    def return_expr(self, args):
        return Expression(args.type_name, go_code=f"return {args.go_code}")

    def open_params(self, args):
        self.symbol_table.push_scope()

    def close_block(self, args):
        self.symbol_table.pop_scope()

    def print_stmt(self, args):
        self.imports.append('"fmt"')
        arg_code = [arg.go_code for arg in args]
        exprs = ",".join(arg_code)
        return f"fmt.Println({exprs})"
