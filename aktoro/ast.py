from dataclasses import dataclass
import aktoro.types as types
from abc import ABC


class Expr(ABC):
    ak_type: types.AkType


@dataclass
class Program:
    statements: list


@dataclass
class VarDecl(Expr):
    name: str
    expr: Expr
    ak_type: types.AkType


@dataclass
class VariantParamDecl(Expr):
    name: str
    index: int
    ak_type: types.AkType


@dataclass
class VarIfAssign(Expr):
    name: str
    expr: Expr
    ak_type: types.AkType


@dataclass
class VarMatchAssign(Expr):
    name: str
    expr: Expr
    ak_type: types.AkType


@dataclass
class VarAssignMut:
    name: str
    expr: Expr


@dataclass
class RecordDecl:
    name: str
    type_params: list
    fields: dict


@dataclass
class VariantDecl:
    name: str
    type_params: list
    constructors: list


@dataclass
class VarUsage(Expr):
    name: str
    ak_type: types.AkType


@dataclass
class FieldAccess(Expr):
    record_name: str
    field_name: str
    ak_type: types.AkType


@dataclass
class PrimitiveLiteral(Expr):
    value: str
    ak_type: types.AkType


@dataclass
class ListLiteral(Expr):
    values: list
    ak_type: types.AkType


@dataclass
class DictLiteral(Expr):
    key_values: list
    ak_type: types.AkType


@dataclass
class KeyValue:
    key: Expr
    value: Expr


@dataclass
class DictUpdate(Expr):
    var: Expr
    updates: list
    ak_type: types.AkType


@dataclass
class RecordLiteral(Expr):
    fields: dict
    ak_type: types.AkType


@dataclass
class VariantLiteral(Expr):
    constructor: types.VariantConstructor
    values: list
    ak_type: types.AkType


@dataclass
class VariantPattern(Expr):
    constructor: str
    ak_type: types.AkType


@dataclass
class VariantTestExpr(Expr):
    name: str
    expr: Expr


@dataclass
class RecordUpdate(Expr):
    var: Expr
    updates: list
    ak_type: types.AkType


@dataclass
class EqualityExpr(Expr):
    left: Expr
    op: str
    right: Expr
    ak_type: types.AkType


@dataclass
class AddExpr(Expr):
    exprs: list
    ak_type: types.AkType


@dataclass
class MultExpr(Expr):
    exprs: list
    ak_type: types.AkType


@dataclass
class ParenExpr(Expr):
    expr: Expr
    ak_type: types.AkType


@dataclass
class NotExpr(Expr):
    expr: Expr
    ak_type: types.AkType


@dataclass
class LogicalExpr(Expr):
    exprs: list
    ak_type: types.AkType


@dataclass
class ParamDecl:
    index: int
    name: str
    ak_type: types.AkType


@dataclass
class RecordDestructParam:
    index: int
    params: list
    parent_type: types.AkType


@dataclass
class FuncDef(Expr):
    name: str
    params: list
    return_type: types.AkType
    body: list
    ak_type: types.AkType


@dataclass
class FuncCall(Expr):
    func_name: str
    args: list
    ak_type: types.AkType


@dataclass
class PrintFunc(Expr):
    ak_type: types.AkType


@dataclass
class PackageVarUsage(Expr):
    package_name: str
    func_name: str
    ak_type: types.AkType


@dataclass
class ReturnStmt(Expr):
    expr: Expr
    ak_type: types.AkType


@dataclass
class ReturnNil:
    pass


@dataclass
class PrintStmt:
    args: list


@dataclass
class ListIndexExpr(Expr):
    var: Expr
    index_expr: Expr
    ak_type: types.AkType


@dataclass
class ListRangeIndexExpr(Expr):
    var: Expr
    index_expr: Expr
    ak_type: types.AkType


@dataclass
class StringIndexExpr(Expr):
    var: Expr
    index_expr: Expr
    ak_type: types.AkType


@dataclass
class StringRangeIndexExpr(Expr):
    var: Expr
    index_expr: Expr
    ak_type: types.AkType


@dataclass
class DictIndexExpr(Expr):
    var: Expr
    index_expr: Expr
    ak_type: types.AkType


@dataclass
class ListConsExpr(Expr):
    var: Expr
    cons_args: list
    ak_type: types.AkType


@dataclass
class RangeIndex:
    low: Expr
    high: Expr


@dataclass
class IfExpr(Expr):
    test_expr: Expr
    if_body: list
    else_body: list
    ak_type: types.AkType


@dataclass
class MatchExpr(Expr):
    test_expr: Expr
    patterns: list
    ak_type: types.AkType


@dataclass
class Pattern(Expr):
    test_expr: Expr
    body: list
    ak_type: types.AkType


@dataclass
class DefaultPattern(Expr):
    body: list
    ak_type: types.AkType


@dataclass
class StringConcat(Expr):
    left: Expr
    right: Expr
    ak_type: types.AkType


@dataclass
class RecordDestructDecl:
    root_var: RecordDecl
    var_decls: dict


@dataclass
class ListDestructDecl:
    root_var: Expr
    var_decls: list
    rest_decl: Expr
