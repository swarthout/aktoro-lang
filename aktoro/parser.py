from lark import Transformer
from lark.tree import Visitor
import aktoro.ast as ast
import aktoro.types as types
import aktoro.builtins as builtins
from aktoro.type_resolver import TypeMapperVisitor, TypeResolverVisitor
from enum import Enum
import copy


class TypeKind(Enum):
    RECORD = 1
    VARIANT = 2
    TYPE_ALIAS = 3


def snake_to_camel(name):
    if name[0] == "_":
        return name
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
            "Int": types.PrimitiveType("Int"),
            "Float": types.PrimitiveType("Float"),
            "String": types.PrimitiveType("String"),
            "Bool": types.PrimitiveType("Bool")
        }, {}]
        self.field_table = {}

    def add(self, name, data):
        self.table[-1][name] = data

    def get(self, name):
        for scope in reversed(self.table):
            if name in scope.keys():
                return scope[name]
        return None

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


class PipelineRewriter(Visitor):
    def pipe_expr(self, tree):
        prev = tree.children[0]
        for i in range(1, len(tree.children)):
            curr = tree.children[i]
            arg_start = 1 if curr.data == 'func_call' else 2
            curr.children.insert(arg_start, prev)
            prev = curr
        tree.data = prev.data
        tree.children = prev.children

    def pipe_record_expr(self, tree):
        self.pipe_expr(tree)


class VariantPatternRewriter(Visitor):
    def pattern(self, tree):
        test_expr, pattern_body = tree.children
        if test_expr.data == "variant_literal":
            test_expr.data = "variant_pattern"
            for i in range(1, len(test_expr.children)):
                param = test_expr.children[i]
                if param == "_":
                    continue
                if param.data == "var_usage":
                    param.data = "variant_param_decl"
                    param.children.insert(0, test_expr.children[0])
                    param.children.insert(1, i - 1)
                pattern_body.children.insert(0, param)
            test_expr.children = test_expr.children[:1]
        tree.children[0] = test_expr
        tree.children[1] = pattern_body


def parse_var_decl(name, expr):
    if isinstance(expr, ast.IfExpr):
        last_if_expr = expr.if_body[-1]
        expr.if_body[-1] = ast.VarAssignMut(name, last_if_expr)
        last_else_expr = expr.else_body[-1]
        expr.else_body[-1] = ast.VarAssignMut(name, last_else_expr)
        return ast.VarIfAssign(name, expr, expr.ak_type)
    if isinstance(expr, ast.MatchExpr):
        for i in range(len(expr.patterns)):
            expr.patterns[i].body[-1] = ast.VarAssignMut(name, expr.patterns[i].body[-1])
        return ast.VarMatchAssign(name, expr, expr.ak_type)

    return ast.VarDecl(name, expr, expr.ak_type)


def resolve_variant_param_decls(patterns, test_expr):
    for pattern in patterns:
        for i, stmt in enumerate(pattern.body):
            if isinstance(stmt, ast.VariantParamDecl):
                expr = ast.FieldAccess(test_expr, f"p{stmt.index}", stmt.ak_type)
                pattern.body[i] = ast.VarDecl(stmt.name, expr, stmt.ak_type)

    return patterns


class Parser(Transformer):
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.imports = []

    def program(self, args):
        args = list(filter(None, args))
        return ast.Program(args)

    def var_decl(self, args):
        name, expr = args
        v = parse_var_decl(name, expr)
        self.symbol_table.add(name, v)
        return v

    def return_stmt(self, args):
        expr = args[0]
        return ast.ReturnStmt(expr, expr.ak_type)

    def record_destruct_decl(self, args):
        vars = args[:-1]
        vars = map(str, vars)
        expr = args[-1]
        v = parse_var_decl("res", expr)
        expr_fields = v.ak_type.fields
        var_decls = {var: ast.VarDecl(var, None, expr_fields[var]) for var in vars}
        for var, var_decl in var_decls.items():
            self.symbol_table.add(var, var_decl)
        return ast.RecordDestructDecl(v, var_decls)

    def list_destruct_decl(self, args):
        vars = args[:-1]
        vars = list(map(str, vars))
        expr = args[-1]
        v = parse_var_decl("res", expr)
        elem_type = v.ak_type.elem_type
        rest_decl = None
        if "|" in vars:
            rest = vars[-1]
            vars = vars[:-2]
            rest_decl = ast.VarDecl(rest, None, v.ak_type)
            self.symbol_table.add(rest, rest_decl)
        var_decls = []
        for var in vars:
            var_decl = ast.VarDecl(var, None, elem_type)
            var_decls.append(var_decl)
            self.symbol_table.add(var, var_decl)
        return ast.ListDestructDecl(v, var_decls, rest_decl)

    def var_name(self, args):
        return str(args[0])

    def var_usage(self, args):
        name = args[0]
        root_var = self.symbol_table.get(name)
        if root_var:
            ak_type = root_var.ak_type
            return ast.VarUsage(name, ak_type)
        else:
            raise NameError(f"name {name} is not defined")

    def field_access(self, args):
        record_name, field_name = args
        parent_ak_type = record_name.ak_type
        ak_type = parent_ak_type.fields[field_name]
        return ast.FieldAccess(record_name, str(field_name), ak_type)

    def index_expr(self, args):
        var, index_expr = args
        if isinstance(var.ak_type, types.ListType):
            if isinstance(index_expr, ast.RangeIndex):
                return ast.ListRangeIndexExpr(var, index_expr, var.ak_type)
            return ast.ListIndexExpr(var, index_expr, var.ak_type.elem_type)
        elif isinstance(var.ak_type, types.DictType):
            ak_type = var.ak_type.val_type
            return ast.DictIndexExpr(var, index_expr, ak_type)
        elif isinstance(var.ak_type, types.PrimitiveType) and var.ak_type.name == "String":
            ak_type = types.PrimitiveType("String")
            if isinstance(index_expr, ast.RangeIndex):
                return ast.StringRangeIndexExpr(var, index_expr, ak_type)
            return ast.StringIndexExpr(var, index_expr, ak_type)
        raise SyntaxError(f"indexing not supported on {var.ak_type}")

    def range_index(self, args):
        low, high = args
        return ast.RangeIndex(low, high)

    def low(self, args):
        if args:
            return args[0]

    def high(self, args):
        if args:
            return args[0]

    def int_literal(self, args):
        return ast.PrimitiveLiteral(args[0], types.PrimitiveType("Int"))

    def float_literal(self, args):
        return ast.PrimitiveLiteral(args[0], types.PrimitiveType("Float"))

    def bool_literal(self, args):
        return ast.PrimitiveLiteral(args[0], types.PrimitiveType("Bool"))

    def string_literal(self, args):
        return ast.PrimitiveLiteral(args[0], types.PrimitiveType("String"))

    def list_literal(self, args):
        elems, *ak_type = args
        if ak_type:
            ak_type = self.type_usage(ak_type)
            return ast.ListLiteral(elems, ak_type)

        if not elems:
            raise TypeError("Must add type annotation to empty list literal")
        elem_type = elems[0].ak_type
        ak_type = types.ListType(elem_type)
        return ast.ListLiteral(elems, ak_type)

    def list_elems(self, args):
        return args

    def list_cons(self, args):
        cons_args, _, var = args
        ak_type = var.ak_type
        return ast.ListConsExpr(var, cons_args, ak_type)

    def cons_args(self, args):
        return args

    def dict_literal(self, args):
        key_values, *ak_type = args
        if ak_type:
            ak_type = self.type_usage(ak_type)
            return ast.DictLiteral(key_values, ak_type)
        else:
            if not key_values:
                raise TypeError("Must add type annotation to empty dict literal")
            first_pair = key_values[0]
            key_type = first_pair.key.ak_type
            val_type = first_pair.value.ak_type
            ak_type = types.DictType(key_type, val_type)
            return ast.DictLiteral(key_values, ak_type)

    def dict_update(self, args):
        var, _, *updates = args
        return ast.DictUpdate(var, updates, var.ak_type)

    def kv_pair_list(self, args):
        return args

    def kv_pair(self, args):
        key, val = args
        return ast.KeyValue(key, val)

    def add_expr(self, args):
        return ast.AddExpr(args, args[0].ak_type)

    def mult_expr(self, args):
        return ast.MultExpr(args, args[0].ak_type)

    def equality_expr(self, args):
        left, op, right = args
        return ast.EqualityExpr(left, op, right, types.PrimitiveType("bool"))

    def equality_record_expr(self, args):
        return self.equality_expr(args)

    def not_expr(self, args):
        _, expr = args
        return ast.NotExpr(expr, expr.ak_type)

    def logical_expr(self, args):
        return ast.LogicalExpr(args, types.PrimitiveType("bool"))

    def paren_expr(self, args):
        return ast.ParenExpr(args[0], args[0].ak_type)

    def type_decl(self, args):
        name, type_params, (type_kind, params) = args
        if type_kind == TypeKind.RECORD:
            fields = dict(params)
            record_decl = ast.RecordDecl(name, type_params, fields)
            record_type = types.RecordType(name, type_params, fields)
            self.symbol_table.add_record(name, record_type)
            return record_decl
        else:
            constructors = params
            if not isinstance(constructors, list):
                constructors = [constructors]
            variant_decl = ast.VariantDecl(name, type_params, constructors)
            variant_type = types.VariantType(name, type_params, constructors)
            self.symbol_table.add(name, variant_type)
            for constructor in constructors:
                constructor.variant_type = variant_type
                self.symbol_table.add(constructor.name, constructor)
            return variant_decl

    def record_def(self, args):
        return TypeKind.RECORD, args[0]

    def variant_def(self, args):
        return TypeKind.VARIANT, list(filter(lambda arg: arg != "|", args))

    def variant_constructor(self, args):
        name, *params = args
        params = [self.type_usage([param]) for param in params] if params else []
        return types.VariantConstructor(str(name), params, None)

    def variant_literal(self, args):
        name, *vars = args
        constructor = self.symbol_table.get(name)
        ak_type = constructor.variant_type
        return ast.VariantLiteral(name, vars, ak_type)

    def variant_pattern(self, args):
        name = args[0]
        constructor = self.symbol_table.get(name)
        ak_type = constructor.variant_type
        return ast.VariantPattern(str(name), ak_type)

    def variant_param_decl(self, args):
        constructor_name, index, var_name = args
        constructor = self.symbol_table.get(constructor_name)
        param_type = constructor.params[index]
        decl = ast.VariantParamDecl(var_name, index, param_type)
        self.symbol_table.add(var_name, decl)
        return decl

    def type_params(self, args):
        params = map(str, args)
        return list(map(types.TypeParameter, params))

    def field_decl(self, args):
        name, *ak_type = args
        ak_type = self.type_usage(ak_type)
        return str(name), ak_type

    def field_list(self, args):
        return args

    def field_name(self, args):
        return str(args[0])

    def type_name(self, args):
        return str(args[0])

    def param_list(self, args):
        return args

    def param(self, args):
        return args[0]

    def type_usage(self, args):
        type_name, *arg_params = args

        if isinstance(type_name, types.AkType):
            return type_name

        if arg_params:
            arg_params = [self.type_usage([param]) for param in arg_params]

        symbol_entry = self.symbol_table.get(type_name)
        ak_type = copy.deepcopy(symbol_entry)
        if not symbol_entry or not isinstance(symbol_entry, types.AkType):
            if type_name == type_name.lower():
                return types.TypeParameter(type_name)

            return types.VariantType(type_name, [], [])

        if isinstance(ak_type, types.ParameterizedType) and ak_type.type_params:
            type_params = ak_type.type_params
            type_resolver = TypeResolverVisitor(
                {param.param: arg for param, arg in zip(type_params, arg_params)})
            ak_type = type_resolver.visit(ak_type)
            ak_type.type_params = arg_params
        return ak_type

    def paren_type(self, args):
        return self.type_usage(args)

    def list_type(self, args):
        elem_type = self.type_usage(args)
        return types.ListType(elem_type)

    def dict_type(self, args):
        key_type, val_type = args
        key_type = self.type_usage([key_type])
        val_type = self.type_usage([val_type])
        return types.DictType(key_type, val_type)

    def func_type(self, args):
        param_types, return_type = args
        if not isinstance(param_types, list):
            param_types = [param_types]
        return types.FuncType(param_types, return_type)

    def param_types(self, args):
        return [self.type_usage([param]) for param in args]

    def param_type(self, args):
        return self.type_usage(args)

    def type_list(self, args):
        return args

    def record_literal(self, args):
        field_dict = dict(args)
        field_names = field_dict.keys()
        record_type = self.symbol_table.get_record_by_field_names(field_names)
        if record_type.type_params:
            field_types = {name: field.ak_type for name, field in field_dict.items()}
            concrete_type = types.RecordType(record_type.name, record_type.type_params, field_types)
            return ast.RecordLiteral(field_dict, concrete_type)
        return ast.RecordLiteral(field_dict, record_type)

    def record_update(self, args):
        var, _, *updates = args
        return ast.RecordUpdate(var, updates, var.ak_type)

    def field_assignment(self, args):
        name, expr = args
        return name, expr

    def func_def(self, args):
        func_name, params, return_type, ak_type = args[0]
        func_body = args[1]

        if isinstance(return_type, types.EmptyTuple):
            func_body.append(ast.ReturnNil())
        elif not isinstance(func_body[-1], ast.ReturnStmt):
            func_body[-1] = self.return_expr(func_body[-1])
        return ast.FuncDef(func_name, params, return_type, func_body, ak_type)

    def func_header(self, args):
        func_name, param_types, return_type = args[0]  # func_signature
        func_name = str(func_name)
        ak_type = types.FuncType(param_types, return_type)
        self.symbol_table.add(func_name, ast.VarUsage(func_name, ak_type))
        self.symbol_table.push_scope()
        param_names = args[2]
        params = {}
        for p_name, p_type in zip(param_names, param_types):
            p_decl = ast.ParamDecl(p_name, p_type)
            params[p_name] = p_decl
            self.symbol_table.add(p_name, p_decl)

        return func_name, params, return_type, ak_type

    def params(self, args):
        return args

    def func_signature(self, args):
        return args

    def simple_return(self, args):
        expr = args[0]
        if isinstance(expr, ast.PrintStmt):
            func_body = [expr]
        else:
            expr = self.return_expr(args[0])
            func_body = [expr]
        self.symbol_table.pop_scope()
        return func_body

    def block(self, args):
        args.pop(0)  # remove open block instruction
        args.pop()  # remove close block instruction
        return args

    def func_call(self, args):
        func, *arg_exprs = args
        func_type = resolve_func_type(copy.deepcopy(func.ak_type), arg_exprs)
        return ast.FuncCall(func, arg_exprs, func_type.return_type)

    def builtin_func_call(self, args):
        package_name, func_name, *arg_exprs = args
        package_name = str(package_name)
        func_name = str(func_name)
        func = builtins.BUILTIN_PACKAGES[package_name][func_name]
        func_type = resolve_func_type(func.ak_type, arg_exprs)
        func_name = ast.PackageVarUsage(package_name, func_name, func_type)
        return ast.FuncCall(func_name, arg_exprs, func_type.return_type)

    def print_func(self, args):
        return ast.PrintFunc(types.FuncType([types.TypeParameter('a')], types.EmptyTuple))

    def return_expr(self, args):
        return ast.ReturnStmt(args, args.ak_type)

    def close_block(self, args):
        self.symbol_table.pop_scope()

    def print_stmt(self, args):
        print_str, *args = args
        return ast.PrintStmt(args)

    def if_expr(self, args):
        test_expr, if_body, *else_body = args
        if else_body:
            else_body = else_body[0]
        last_if_expr = if_body[-1]
        if isinstance(last_if_expr, ast.Expr):
            ak_type = if_body[-1].ak_type
        else:
            ak_type = None
        return ast.IfExpr(test_expr, if_body, else_body, ak_type)

    def if_body(self, args):
        return args

    def else_expr(self, args):
        return args

    def match_expr(self, args):
        if len(args) == 2:
            test_expr, patterns = args
            if isinstance(test_expr.ak_type, types.VariantType):
                var_name = "_v"
                patterns = resolve_variant_param_decls(patterns, ast.VarUsage(var_name, test_expr.ak_type))
                test_expr = ast.VariantTestExpr(var_name, test_expr)
            return ast.MatchExpr(test_expr, patterns, patterns[0].ak_type)
        else:
            patterns = args[0]
            return ast.MatchExpr(None, patterns, patterns[0].ak_type)

    def test_expr(self, args):
        return args[0]

    def match_patterns(self, args):
        return args

    def pattern(self, args):
        expr, body = args
        last_expr = body[-1]
        if isinstance(last_expr, ast.Expr):
            ak_type = last_expr.ak_type
        else:
            ak_type = None
        return ast.Pattern(expr, body, ak_type)

    def pattern_default(self, args):
        underscore, body = args
        last_expr = body[-1]
        if isinstance(last_expr, ast.Expr):
            ak_type = last_expr.ak_type
        else:
            ak_type = None
        return ast.DefaultPattern(body, ak_type)

    def pattern_body(self, args):
        return args

    def string_concat(self, args):
        left, right = args
        return ast.StringConcat(left, right, left.ak_type)

    def empty_tuple(self, args):
        return types.EmptyTuple()


def resolve_func_type(func_type, args):
    arg_types = map(lambda arg: arg.ak_type, args)
    type_mapper = TypeMapperVisitor()
    for f_type, a_type in zip(func_type.param_types, arg_types):
        type_mapper.visit(f_type, a_type)
    param_map = type_mapper.get_param_map()
    type_resolver = TypeResolverVisitor(param_map)
    for f_type in func_type.param_types:
        type_resolver.visit(f_type)
    func_type.return_type = type_resolver.visit(func_type.return_type)
    return func_type
