from lark import Transformer
from ak_ast import *
from ak_types import *


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
        self.table = [{
            "int": PrimitiveType("int"),
            "float": PrimitiveType("float"),
            "string": PrimitiveType("string"),
            "bool": PrimitiveType("bool")
        }, {}]
        self.field_table = {}

    def add(self, name, data):
        self.table[-1][name] = data

    def get(self, name):
        for scope in reversed(self.table):
            if name in scope.keys():
                return scope[name]
        raise KeyError(name)

    def push_scope(self):
        self.table.append({})

    def pop_scope(self):
        self.table.pop()

    @staticmethod
    def hash_field_names(field_names):
        fields_sorted = sorted(field_names)
        field_hash = "#".join(fields_sorted)
        return field_hash

    def get_record_by_field_names(self, field_names):
        field_hash = self.hash_field_names(field_names)
        record_name = self.field_table[field_hash]
        return self.get(record_name)

    def add_record(self, name, record):
        field_names = list(record.fields.keys())
        field_hash = self.hash_field_names(field_names)
        self.add(name, record)
        self.field_table[field_hash] = name

    def get_variant_by_constructor(self, constructor):
        pass


class Parser(Transformer):
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.imports = []

    def program(self, args):
        args = list(filter(None, args))
        return Program(args)

    def var_decl(self, args):
        name, expr = args
        v = VarDecl(name, expr, expr.ak_type)
        self.symbol_table.add(name, v)
        return v

    def var_name(self, args):
        return str(args[0])

    def var_usage(self, args):
        root_name = args[0]
        root_var = self.symbol_table.get(root_name)
        ak_type = root_var.ak_type
        if len(args) > 1:
            for arg in args[1:]:
                record = self.symbol_table.get(ak_type.name)
                ak_type = record.fields[arg]
        name = ".".join(args)
        return VarUsage(name, ak_type)

    def index_expr(self, args):
        var, index_expr = args
        if isinstance(var.ak_type, ListType):
            ak_type = var.ak_type.elem_type
        elif isinstance(var.ak_type, DictType):
            ak_type = var.ak_type.val_type
        return IndexExpr(var, index_expr, ak_type)

    def range_index(self, args):
        low, high = args
        return RangeIndex(low, high)

    def low(self, args):
        if args:
            return args[0]

    def high(self, args):
        if args:
            return args[0]

    def int_literal(self, args):
        return PrimitiveLiteral(args[0], PrimitiveType("int"))

    def float_literal(self, args):
        return PrimitiveLiteral(args[0], PrimitiveType("float"))

    def bool_literal(self, args):
        return PrimitiveLiteral(args[0], PrimitiveType("bool"))

    def string_literal(self, args):
        return PrimitiveLiteral(args[0], PrimitiveType("string"))

    def list_literal(self, args):
        if len(args) == 2:
            elems, ak_type = args
            return ListLiteral(elems, ak_type)
        else:
            elems = args[0]
            if not elems:
                raise TypeError("Must add type annotation to empty list literal")
            elem_type = elems[0].ak_type
            ak_type = ListType(elem_type)
            return ListLiteral(elems, ak_type)

    def list_elems(self, args):
        return args

    def list_cons(self, args):
        cons_args, var = args
        ak_type = var.ak_type
        return ListConsExpr(var, cons_args, ak_type)

    def cons_args(self, args):
        return args

    def dict_literal(self, args):
        if len(args) == 2:
            key_values = args[0]
            ak_type = args[1]
            return DictLiteral(key_values, ak_type)
        else:
            key_values = args[0]
            if not key_values:
                raise TypeError("Must add type annotation to empty dict literal")
            first_pair = key_values[0]
            key_type = first_pair.key.ak_type
            val_type = first_pair.value.ak_type
            ak_type = DictType(key_type, val_type)
            return DictLiteral(key_values, ak_type)

    def dict_update(self, args):
        var = args[0]
        updates = args[1:]
        return DictUpdate(var, updates, var.ak_type)

    def kv_pair_list(self, args):
        return args

    def kv_pair(self, args):
        key, val = args
        return KeyValue(key, val)

    def add_expr(self, args):
        left, op, right = args
        return BinaryOpExpr(left, op, right, left.ak_type)

    def mult_expr(self, args):
        left, op, right = args
        return BinaryOpExpr(left, op, right, left.ak_type)

    def type_decl(self, args):
        name, (type_kind, fields) = args
        if type_kind == TypeKind.RECORD:
            fields = dict(fields)
            record_decl = RecordDecl(name, [], fields)
            record_type = RecordType(name, [], fields)
            self.symbol_table.add_record(name, record_type)
            return record_decl
        raise NotImplemented("variants not implemented!")

    def record_def(self, args):
        return TypeKind.RECORD, args[0]

    def type_name(self, args):
        return str(args[0])

    def param_list(self, args):
        return args

    def param(self, args):
        name, ak_type = args
        param_decl = ParamDecl(name, ak_type)
        self.symbol_table.add(name, param_decl)
        return name, param_decl

    def build_ak_type(self, args):
        ak_type = None
        type_name = args[0]
        if isinstance(type_name, AkType):
            return type_name
        if type_name == "list":
            elem_type = self.build_ak_type(args[1:])
            ak_type = ListType(elem_type)
        elif type_name == "dict":
            key_type = self.build_ak_type([args[1]])
            val_type = self.build_ak_type([args[2]])
            ak_type = DictType(key_type, val_type)
        else:
            symbol_entry = self.symbol_table.get(type_name)
            if isinstance(symbol_entry, PrimitiveType):
                ak_type = symbol_entry
            else:
                ak_type = RecordType(type_name, [], {})
        return ak_type

    def type_usage(self, args):
        ak_type = self.build_ak_type(args)
        return ak_type

    def record_literal(self, args):
        field_dict = dict(args)
        field_names = field_dict.keys()
        record_type = self.symbol_table.get_record_by_field_names(field_names)
        return RecordLiteral(field_dict, record_type)

    def field_assignment(self, args):
        name, expr = args
        return name, expr

    def field_decl(self, args):
        name, type_name = args
        return str(name), type_name

    def field_list(self, args):
        return args

    def field_name(self, args):
        return str(args[0])

    def func_def(self, args):
        _, params, _, return_type, func_body = args
        params = dict(params)
        ak_type = FuncType(params, return_type)
        return FuncDef(params, return_type, func_body, ak_type)

    def func_body(self, args):
        args.pop(0)  # remove open block instruction
        args.pop()  # remove close block instruction
        last_expr = args[-1]
        last_expr = self.return_expr(last_expr)
        args[-1] = last_expr
        return args

    def func_call(self, args):
        var_usage, *arg_exprs = args
        return FuncCall(var_usage, arg_exprs, var_usage.ak_type.return_type)

    def return_expr(self, args):
        return ReturnExpr(args, args.ak_type)

    def open_params(self, args):
        self.symbol_table.push_scope()

    def close_block(self, args):
        self.symbol_table.pop_scope()

    def print_stmt(self, args):
        return PrintStmt(args)
