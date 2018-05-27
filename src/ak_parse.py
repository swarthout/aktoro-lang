from lark import Transformer
from collections import namedtuple
import textwrap
from enum import Enum
from abc import ABC, abstractmethod
from .ak_ast import *

Expression = namedtuple('Expression', ['type_name', 'go_code'])
Statement = namedtuple('Statement', ['go_code'])
Variable = namedtuple('Variable', ['name', 'type_name'])
Record = namedtuple('Record', ['name', 'fields'])

PRIMITIVE_TYPES = ["int", "float", "string", "bool"]


class TypeKind(Enum):
    RECORD = 1
    VARIANT = 2
    TYPE_ALIAS = 3


class AkType(ABC):

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def get_go_type_usage(self):
        pass


class ListType(AkType):
    def __init__(self, name, elem_type):
        super().__init__(name)
        self.elem_type = elem_type

    def get_go_type_usage(self):
        return "[]{}".format(self.elem_type.get_go_type_usage())


class PrimitiveType(AkType):
    # map primitive aktoro types to their golang equivalents
    primitive_types = {
        "int": "int",
        "float": "float64",
        "string": "string",
        "bool": "bool"
    }

    def __init__(self, name):
        super().__init__(name)

    def get_go_type_usage(self):
        if self.name in self.primitive_types:
            return self.primitive_types[self.name]


class DictType(AkType):
    def __init__(self, name, key_type, val_type):
        super().__init__(name)
        self.key_type = key_type
        self.val_type = val_type

    def get_go_type_usage(self):
        return "map[{}]{}".format(self.key_type, self.val_type)


class RecordType(AkType):
    def __init__(self, name, type_params, fields):
        super().__init__(name)
        self.type_params = type_params
        self.fields = fields

    def get_go_type_usage(self):
        return snake_to_camel(self.name)

    def get_go_type_def(self, type_args):
        """
        Gets a go struct definition for a given record
        :param type_args: dict of type_param to specialized type
        :return: specialized go struct
        """
        pass


class VariantType(AkType):
    pass


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


class TypeDefTable:
    def __init__(self):
        self.field_table = {}
        self.name_table = {}

    @staticmethod
    def hash_field_names(field_names):
        fields_sorted = sorted(field_names)
        field_hash = "#".join(fields_sorted)
        return field_hash

    def get_record_by_name(self, name):
        if name not in self.name_table:
            return
        field_hash = self.name_table[name]
        if field_hash not in self.field_table:
            return
        return self.field_table[field_hash]

    def get_by_field_names(self, field_names):
        field_hash = self.hash_field_names(field_names)
        return self.field_table[field_hash]

    def insert_record(self, record):
        field_names = list(record.fields.keys())
        field_hash = self.hash_field_names(field_names)
        self.name_table[record.name] = field_hash
        self.field_table[field_hash] = record


class Parser(Transformer):
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.type_def_table = TypeDefTable()
        self.imports = []
        self.module_type_defs = []

    def program(self, args):
        args = filter(None, args)
        return Program(args)

    def decl(self, args):
        name, expr = args
        return VarDecl(name, expr, expr.ak_type)

    def var_decl(self, args):
        return snake_to_camel(args[0])

    def var_usage(self, args):
        name = ".".join(args)
        return VarUsage(name, ak_type=None)  # ak_type is not known until type checking

    def list_index(self, args):
        var, index_expr = args
        return IndexExpr(var, index_expr)

    def int_literal(self, args):
        return PrimitiveLiteral(value=args[0], ak_type=PrimitiveType("int"))

    def float_literal(self, args):
        return PrimitiveLiteral(value=args[0], ak_type=PrimitiveType("float"))

    def bool_literal(self, args):
        return PrimitiveLiteral(value=args[0], ak_type=PrimitiveType("bool"))

    def string_literal(self, args):
        return PrimitiveLiteral(value=args[0], ak_type=PrimitiveType("string"))

    def list_literal(self, args):
        if not args:
            raise NotImplemented("empty list literals not implemented yet!")
        elem_type = args[0].ak_type
        ak_type = ListType(elem_type)
        return ListLiteral(args, ak_type)

    def add_expr(self, args):
        left, op, right = args
        go_code = f"{left.go_code} {op} {right.go_code}"
        return BinaryOpExpr(left, op, right, left.ak_type)

    def mult_expr(self, args):
        left, op, right = args
        go_code = f"{left.go_code} {op} {right.go_code}"
        return BinaryOpExpr(left, op, right, left.ak_type)

    def type_def(self, args):
        name, body = args
        if body["type_kind"] == TypeKind.RECORD:
            r = Record(name=name, fields={})
            field_defs = body["field_defs"]
            for f in field_defs:
                r.fields[f["name"]] = f["type_name"]
            self.symbol_table.add_symbol(name, r)
            self.type_def_table.insert_record(r)
            field_go_code = [f["go_code"] for f in field_defs]
            field_go_code = textwrap.indent("\n".join(field_go_code), "\t")
            go_code = textwrap.dedent("""
            type {name} struct {{
            {fields}
            }}
            """)
            self.module_type_defs.append(
                Statement(go_code.format(name=name, fields=field_go_code)))

    def record_def(self, args):
        return {
            "type_kind": TypeKind.RECORD,
            "field_defs": args[0]
        }

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

    def build_ak_type(self, args):
        ak_type = None
        type_name = args[0]
        if isinstance(type_name, AkType):
            return type_name
        if type_name in PRIMITIVE_TYPES:
            ak_type = PrimitiveType(type_name)
        elif type_name == "list":
            elem_type = self.build_ak_type(args[1:])
            ak_type = ListType(type_name, elem_type)
        record = self.type_def_table.get_record_by_name(type_name)
        if record:
            ak_type = RecordType(type_name, [], {})
        return ak_type

    def type_usage(self, args):
        ak_type = self.build_ak_type(args)
        return ak_type.get_go_type_usage()

    def record_literal(self, args):
        field_dict = dict(args)
        record = self.type_def_table.get_by_field_names(field_names)
        fields_go_code = ",\n".join([field["go_code"] for field in args])
        go_code = f"{record.name}{{\n" + \
                  textwrap.indent(fields_go_code, "\t") + textwrap.dedent("}")
        return Expression(type_name=record.name, go_code=go_code)

    def field_assignment(self, args):
        name, expr = args
        return name, expr

    def field_decl(self, args):
        name, type_name = args
        return name, type_name

    def field_list(self, args):
        return args

    def field_name(self, args):
        return args[0]

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
        go_code = go_code.format(
            params=params, return_type=return_type, func_body=func_body)
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
        if '"fmt"' not in self.imports:
            self.imports.append('"fmt"')
        arg_code = [arg.go_code for arg in args]
        exprs = ",".join(arg_code)
        return Statement(f"fmt.Println({exprs})")
