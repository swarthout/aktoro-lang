from lark import Transformer
from aktoro.ast import *
from aktoro.types import *


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
            "Int": PrimitiveType("Int"),
            "Float": PrimitiveType("Float"),
            "String": PrimitiveType("String"),
            "Bool": PrimitiveType("Bool")
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
        if isinstance(expr, IfExpr):
            last_if_expr = expr.if_body[-1]
            expr.if_body[-1] = VarAssignMut(name, last_if_expr)
            last_else_expr = expr.else_body[-1]
            expr.else_body[-1] = VarAssignMut(name, last_else_expr)
            v = VarIfAssign(name, expr, expr.ak_type)
        else:
            v = VarDecl(name, expr, expr.ak_type)
        self.symbol_table.add(name, v)
        return v

    def var_name(self, args):
        return str(args[0])

    def var_usage(self, args):
        name = args[0]
        root_var = self.symbol_table.get(name)
        ak_type = root_var.ak_type
        return VarUsage(name, ak_type)

    def field_access(self, args):
        record_name, field_name = args
        parent_ak_type = self.symbol_table.get(record_name.ak_type.name)
        ak_type = parent_ak_type.fields[field_name]
        return FieldAccess(record_name, str(field_name), ak_type)

    def index_expr(self, args):
        var, index_expr = args
        if isinstance(var.ak_type, ListType):
            ak_type = var.ak_type.elem_type
            if isinstance(index_expr, RangeIndex):
                return ListRangeIndexExpr(var, index_expr, ak_type)
            return ListIndexExpr(var, index_expr, ak_type)
        elif isinstance(var.ak_type, DictType):
            ak_type = var.ak_type.val_type
            return DictIndexExpr(var, index_expr, ak_type)

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
        return PrimitiveLiteral(args[0], PrimitiveType("Int"))

    def float_literal(self, args):
        return PrimitiveLiteral(args[0], PrimitiveType("Float"))

    def bool_literal(self, args):
        return PrimitiveLiteral(args[0], PrimitiveType("Bool"))

    def string_literal(self, args):
        return PrimitiveLiteral(args[0], PrimitiveType("String"))

    def list_literal(self, args):
        elems, *ak_type = args
        if ak_type:
            return ListLiteral(elems, ak_type[0])
        else:
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
        key_values, *ak_type = args
        if ak_type:
            return DictLiteral(key_values, ak_type[0])
        else:
            if not key_values:
                raise TypeError("Must add type annotation to empty dict literal")
            first_pair = key_values[0]
            key_type = first_pair.key.ak_type
            val_type = first_pair.value.ak_type
            ak_type = DictType(key_type, val_type)
            return DictLiteral(key_values, ak_type)

    def dict_update(self, args):
        var, *updates = args
        return DictUpdate(var, updates, var.ak_type)

    def kv_pair_list(self, args):
        return args

    def kv_pair(self, args):
        key, val = args
        return KeyValue(key, val)

    def add_expr(self, args):
        return AddExpr(args, args[0].ak_type)

    def mult_expr(self, args):
        return MultExpr(args, args[0].ak_type)

    def equality_expr(self, args):
        left, op, right = args
        return EqualityExpr(left, op, right, PrimitiveType("bool"))

    def paren_expr(self, args):
        return ParenExpr(args[0])

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
        return args[0]

    def build_ak_type(self, args):
        ak_type = None
        type_name = args[0]
        if isinstance(type_name, AkType):
            return type_name
        if type_name == "List":
            elem_type = self.build_ak_type(args[1:])
            ak_type = ListType(elem_type)
        elif type_name == "Dict":
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

    def list_type(self, args):
        elem_type = args[0]
        return ListType(elem_type)

    def dict_type(self, args):
        key_type, val_type = args
        return DictType(key_type, val_type)

    def func_type(self, args):
        param_types, return_type = args
        if not isinstance(param_types, list):
            param_types = [param_types]
        return FuncType(param_types, return_type)

    def type_list(self, args):
        return args

    def record_literal(self, args):
        field_dict = dict(args)
        field_names = field_dict.keys()
        record_type = self.symbol_table.get_record_by_field_names(field_names)
        return RecordLiteral(field_dict, record_type)

    def record_update(self, args):
        var, *updates = args
        return RecordUpdate(var, updates, var.ak_type)

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
        func_name, params, return_type, ak_type = args[0]
        func_body = args[1]
        return FuncDef(func_name, params, return_type, func_body, ak_type)

    def func_header(self, args):
        func_name, param_types, return_type = args[0]  # func_signature
        func_name = str(func_name)
        ak_type = FuncType(param_types, return_type)
        self.symbol_table.add(func_name, VarUsage(func_name, ak_type))
        self.symbol_table.push_scope()
        param_names = args[2]
        params = {}
        for p_name, p_type in zip(param_names, param_types):
            p_decl = ParamDecl(p_name, p_type)
            params[p_name] = p_decl
            self.symbol_table.add(p_name, p_decl)

        return func_name, params, return_type, ak_type

    def param_types(self, args):
        return args

    def params(self, args):
        return args

    def func_signature(self, args):
        return args

    def simple_return(self, args):
        expr = self.return_expr(args[0])
        self.symbol_table.pop_scope()
        return [expr]

    def block(self, args):
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
        return ReturnStmt(args, args.ak_type)

    def open_params(self, args):
        # self.symbol_table.push_scope()
        pass

    def close_block(self, args):
        self.symbol_table.pop_scope()

    def print_stmt(self, args):
        return PrintStmt(args)

    def if_expr(self, args):
        test_expr, if_body, *else_body = args
        if else_body:
            else_body = else_body[0]
        last_if_expr = if_body[-1]
        if isinstance(last_if_expr, Expr):
            ak_type = if_body[-1].ak_type
        else:
            ak_type = None
        return IfExpr(test_expr, if_body, else_body, ak_type)

    def if_body(self, args):
        return args

    def else_expr(self, args):
        return args

    def string_concat(self, args):
        left, right = args
        return StringConcat(left, right, left.ak_type)

    def pipe_expr(self, args):
        prev = args[0]
        for i in range(1, len(args)):
            curr = args[i]
            curr.args.insert(0, prev)
            prev = curr

        return prev
