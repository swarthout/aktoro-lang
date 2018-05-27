from lark import Transformer
from collections import ChainMap
from .ak_ast import *
from .ak_types import *

PRIMITIVE_TYPES = {
    "int": PrimitiveType("int"),
    "float": PrimitiveType("float"),
    "string": PrimitiveType("string"),
    "bool": PrimitiveType("bool")
}


class TypeKind(Enum):
    RECORD = 1
    VARIANT = 2
    TYPE_ALIAS = 3


def snake_to_camel(name):
    words = name.split("_")
    if len(words) > 1:
        camel_name = words[0] + "".join(map(str.capitalize, words[1:]))
    else:
        camel_name = words[0]
    return camel_name


class SymbolTable(object):
    """
    Class representing a symbol table.  It should provide functionality
    for adding and looking up nodes associated with identifiers.
    """

    def __init__(self):
        self.table = ChainMap()
        self.current_scope = self.table
        self.root_scope = self.table

    def add(self, symbol, data):
        self.current_scope[symbol] = data

    def get(self, symbol):
        if symbol in self.current_scope:
            return self.current_scope[symbol]
        return None

    def push_scope(self):
        self.current_scope = self.table.new_child()
        return self.current_scope

    def pop_scope(self):
        self.current_scope = self.current_scope.parents
        return self.current_scope

    def pprint(self):
        print("{}top".format("-" * 10))
        for symbol in self.table:
            print("{}: {}".format(symbol, self.table.get(symbol)))
        print("-" * 10)


class Parser(Transformer):
    def __init__(self):
        self.symbol_table = SymbolTable()
        # self.record_table = RecordTable()
        self.imports = []
        # self.module_type_defs = []

        self.field_table = {}

    @staticmethod
    def hash_field_names(field_names):
        fields_sorted = sorted(field_names)
        field_hash = "#".join(fields_sorted)
        return field_hash

    def get_record_by_name(self, name):
        return self.symbol_table.get(name)

    def get_record_by_field_names(self, field_names):
        field_hash = self.hash_field_names(field_names)
        record_name = self.field_table[field_hash]
        return self.symbol_table.get(record_name)

    def insert_record(self, name, record):
        field_names = list(record.fields.keys())
        field_hash = self.hash_field_names(field_names)
        self.symbol_table.add(name, record)
        self.field_table[field_hash] = name

    def get_variant_by_constructor(self, constructor):
        pass

    def program(self, args):
        args = filter(None, args)
        return Program(args)

    def var_decl(self, args):
        name, expr = args
        v = VarDecl(name, expr, expr.ak_type)
        self.symbol_table.add(name, v)
        return v

    def var_name(self, args):
        return args[0]

    def var_usage(self, args):
        root_name = args[0]
        root_var = self.symbol_table.get(root_name)
        ak_type = root_var.ak_type
        if len(args) > 1:
            for arg in args[1:]:
                record = self.get_record_by_name(ak_type)
                ak_type = record.fields[arg]
        name = ".".join(args)
        return VarUsage(name, ak_type)

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
            raise NotImplemented("empty list literals not implemented!")
        elem_type = args[0].ak_type
        ak_type = ListType(elem_type)
        return ListLiteral(args, ak_type)

    def add_expr(self, args):
        left, op, right = args
        return BinaryOpExpr(left, op, right, left.ak_type)

    def mult_expr(self, args):
        left, op, right = args
        return BinaryOpExpr(left, op, right, left.ak_type)

    def type_def(self, args):
        name, (type_kind, fields) = args
        if type_kind == TypeKind.RECORD:
            fields = dict(fields)
            r = RecordType(name, [], fields)
            self.insert_record(name, r)
            return r
        raise NotImplemented("variants not implemented!")

    def record_def(self, args):
        return TypeKind.RECORD, args[0]

    def type_decl(self, args):
        return args[0]

    def param_list(self, args):
        return args

    def param(self, args):
        name, type_name = args
        return name, type_name

    def build_ak_type(self, args):
        ak_type = None
        type_name = args[0]
        if isinstance(type_name, AkType):
            return type_name
        if type_name in PRIMITIVE_TYPES:
            ak_type = PrimitiveType(type_name)
        elif type_name == "list":
            elem_type = self.build_ak_type(args[1:])
            ak_type = ListType(elem_type)
        record = self.get_record_by_name(type_name)
        if record:
            ak_type = RecordType(type_name, [], {})
        return ak_type

    def type_usage(self, args):
        ak_type = self.build_ak_type(args)
        return ak_type.get_go_type_usage()

    def record_literal(self, args):
        field_dict = dict(args)
        field_names = field_dict.keys()
        record_type = self.get_record_by_field_names(field_names)
        return RecordType(record_type, [], field_dict)

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
