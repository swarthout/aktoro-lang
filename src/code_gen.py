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
        self.table = {}

    def set(self, name, data):
        self.table[name] = data

    def get(self, name):
        return self.table[name]


class RecordTable:
    def __init__(self):
        self.table = {}
        self.name_table = {}

    @staticmethod
    def hash_fields(fields):
        fields_sorted = sorted(fields)
        field_hash = "#".join(fields_sorted)
        return field_hash

    def get_record_by_name(self, name):
        field_hash = self.name_table[name]
        return self.table[field_hash]

    def get_record_by_fields(self, fields):
        field_hash = self.hash_fields(fields)
        return self.table[field_hash]

    def insert_record(self, name, fields):
        field_hash = self.hash_fields(fields)
        self.name_table[name] = field_hash
        self.table[field_hash] = Record(name=name, fields=fields)


class CodeGen(Transformer):
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.record_table = RecordTable()

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
        self.symbol_table.set(name, Variable(name, expr.type_name))
        return f"{name} := {expr.go_code}"

    def var_decl(self, args):
        return snake_to_camel(args[0])

    def var_usage(self, args):
        return snake_to_camel(args[0])

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
        name, field_defs = args
        r = Record(name=name, fields={})
        for f in field_defs:
            r.fields[f["name"]] = f["type_name"]
        self.symbol_table.set(name, r)
        self.record_table.insert_record(name, [f["name"] for f in field_defs])
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
        return {
            "name": name,
            "type_name": type_name,
            "go_code": f"{name} {type_name}"
        }

    def type_usage(self, args):
        return snake_to_camel(args[0])

    def record_usage(self, args):
        field_names = [field["name"] for field in args]
        record = self.record_table.get_record_by_fields(field_names)
        fields_go_code = "\n".join([field["go_code"] for field in args])
        go_code = f"{record.name}{{\n" + textwrap.indent(fields_go_code, "\t") + textwrap.dedent("\n}")
        return Expression(type_name=record.name, go_code=go_code)

    def field_assignment(self, args):
        name, expr = args
        return {
            "name": name,
            "expr": expr,
            "go_code": f"{name}: {expr.go_code}"
        }
