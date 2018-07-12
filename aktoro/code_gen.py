import textwrap
from aktoro.ast import *
from aktoro.parser import snake_to_camel
import aktoro.types as types


class CodeGenVisitor():

    def __init__(self):
        self.imports = set()

    def visit(self, node):
        '''
        Execute a method of the form visit_NodeName(node) where
        NodeName is the name of the class of a particular node.
        '''
        if node:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method)
            return visitor(node)
        else:
            return None

    def visit_Program(self, node):

        record_decls = []
        func_defs = []
        main_statements = []
        for line in node.statements:
            if isinstance(line, RecordDecl) or isinstance(line, VariantDecl):
                record_decls.append(line)
            elif isinstance(line, FuncDef):
                func_defs.append(line)
            elif line is not None:
                main_statements.append(line)
        main_go_code = "\n".join([self.visit(s) for s in main_statements])
        record_decl_go_code = "\n".join([self.visit(r) for r in record_decls])
        func_def_go_code = "\n".join([self.visit(f) for f in func_defs])
        imports_go_code = "\n".join(list(self.imports))

        go_body = textwrap.dedent("""
                    package main
                    import (
                    {imports}
                    )
                    {record_decls}
                    {func_defs}
                    func main() {{
                    {main_code}
                    }}

                    """)
        return go_body.format(main_code=textwrap.indent(main_go_code, "\t"),
                              record_decls=record_decl_go_code,
                              func_defs=func_def_go_code,
                              imports=imports_go_code)

    def visit_VarDecl(self, node):
        node_name = snake_to_camel(node.name)
        return f"{node_name} := {self.visit(node.expr)}"

    def visit_VarIfAssign(self, node):
        var_decl = self.visit_VarDeclNoInit(node)

        return var_decl + "\n" + self.visit(node.expr)

    def visit_VarMatchAssign(self, node):
        var_decl = self.visit_VarDeclNoInit(node)

        return var_decl + "\n" + self.visit(node.expr)

    def visit_VarDeclNoInit(self, node):
        node_name = snake_to_camel(node.name)
        return f"var {node_name} {node.ak_type.go_code()}"

    def visit_VarAssignMut(self, node):
        node_name = snake_to_camel(node.name)
        expr = self.visit(node.expr)
        return f"{node_name} = {expr}"

    def visit_RecordDecl(self, node):
        fields = "\n".join([f"{name} {ak_type.go_code()}" for name, ak_type in node.fields.items()])
        fields = textwrap.indent(fields, "\t")
        go_code = textwrap.dedent("""
        type {name} struct {{
        {fields}
        }}
        """)
        return go_code.format(name=node.name, fields=fields)

    def visit_VariantDecl(self, node):
        variant_go_code = textwrap.dedent(f""" 
        type {node.name} interface {{ 
            {node.name}()
        }}
        """)

        constructor_go_code = []
        for constructor in node.constructors:
            constructor_params = "; ".join([
                f"p{i} {param.go_code()}"
                for i, param in enumerate(constructor.params)
            ])
            constructor_params = textwrap.indent(constructor_params, "\t")
            constructor_go_code.append(textwrap.dedent(f"""
            type {constructor.name} struct {{ 
            {constructor_params}
            }}
            
            func ({constructor.name}) {node.name}() {{}}
            """))
        return variant_go_code + "\n".join(constructor_go_code)

    def visit_VariantLiteral(self, node):
        vals = [self.visit(val) for val in node.values]
        vals = ",\n".join([textwrap.indent(f, "\t") for f in vals])
        go_code = f"{node.constructor}{{\n" + textwrap.indent(vals, "\t") + textwrap.dedent("}")
        return go_code

    def visit_VarUsage(self, node):

        return snake_to_camel(node.name)

    def visit_PackageVarUsage(self, node):
        name = snake_to_camel(node.func_name)
        name = name[:1].upper() + name[1:]
        return f"{node.package_name}.{name}"

    def visit_FieldAccess(self, node):
        return f"{self.visit(node.record_name)}.{snake_to_camel(node.field_name)}"

    def visit_PrimitiveLiteral(self, node):
        self.imports.add('"github.com/aktoro-lang/types"')
        literal_type = node.ak_type.name
        if literal_type == "String":
            return f"types.AkString({node.value})"
        elif literal_type == "Int":
            return f"types.AkInt({node.value})"
        elif literal_type == "Float":
            return f"types.AkFloat({node.value})"
        elif literal_type == "Bool":
            return f"types.AkBool({node.value})"
        else:
            raise TypeError("unhandled primitive type")

    def visit_ListLiteral(self, node):
        self.imports.add('"github.com/aktoro-lang/container/list"')
        elems = [self.visit(elem) for elem in node.values]
        elem_go_code = ", ".join(elems)
        return f"list.New({elem_go_code})"

    def visit_DictLiteral(self, node):
        self.imports.add('"github.com/aktoro-lang/container/dict"')
        kv_pairs = [self.visit(kv) for kv in node.key_values]
        kv_pairs_go_code = ",\n".join(kv_pairs)
        return f"dict.New({kv_pairs_go_code})"

    def visit_KeyValue(self, node):
        return f"dict.NewKeyValue({self.visit(node.key)},{self.visit(node.value)})"

    def visit_DictUpdate(self, node):
        updates_go_code = ",".join([self.visit(update) for update in node.updates])
        return f"dict.Put({self.visit(node.var)}, {updates_go_code})"

    def visit_RecordLiteral(self, node):
        fields = [f"{name}: {self.visit(expr)}" for name, expr in node.fields.items()]
        fields = ",\n".join([textwrap.indent(f, "\t") for f in fields])
        record_type = node.ak_type.go_code()
        go_code = f"{record_type}{{\n" + textwrap.indent(fields, "\t") + textwrap.dedent("}")
        return go_code

    def visit_RecordUpdate(self, node):
        record_type = node.ak_type.go_code()
        updated_fields = set([field for field, value in node.updates])
        all_fields = set(node.ak_type.fields.keys())
        unchanged_fields = all_fields - updated_fields
        unchanged_fields = [f"{name}: {self.visit(node.var)}.{name}" for name in unchanged_fields]
        updated_fields = [f"{name}: {self.visit(expr)}" for name, expr in node.updates]
        all_fields = unchanged_fields + updated_fields
        fields_go_code = ",\n".join([textwrap.indent(f, "\t") for f in all_fields])
        go_code = f"{record_type}{{\n" + textwrap.indent(fields_go_code, "\t") + textwrap.dedent("}")
        return go_code

    def visit_EqualityExpr(self, node):
        return f"types.AkBool({self.visit(node.left)} {node.op} {self.visit(node.right)})"

    def visit_AddExpr(self, node):
        exprs = []
        for e in node.exprs:
            if e in ["+", "-"]:
                exprs.append(e)
            else:
                exprs.append(self.visit(e))
        return " ".join(exprs)

    def visit_MultExpr(self, node):
        exprs = []
        for e in node.exprs:
            if e in ["*", "/", "%"]:
                exprs.append(e)
            else:
                exprs.append(self.visit(e))
        return " ".join(exprs)

    def visit_LogicalExpr(self, node):
        operators = {
            "and": "&&",
            "or": "||"
        }
        exprs = []
        for e in node.exprs:
            if e in operators.keys():
                exprs.append(operators[e])
            else:
                exprs.append(self.visit(e))
        return " ".join(exprs)

    def visit_NotExpr(self, node):
        return f"types.AkBool(!{self.visit(node.expr)})"

    def visit_ParenExpr(self, node):
        return f"({self.visit(node.expr)})"

    def visit_ParamDecl(self, node):
        return f"{snake_to_camel(node.name)} {node.ak_type.go_code()}"

    def visit_FuncDef(self, node):
        param_interfaces = ", ".join([f"p{i} interface{{}}" for i in range(len(node.params))])
        params = []
        for i, param in enumerate(node.params.values()):
            params.append(f"{param.name} := p{i}.({param.ak_type.go_code()})")
        params = "\n".join(params)
        return_type = "interface{}"
        func_name = snake_to_camel(node.name)
        func_body = "\n".join([self.visit(line) for line in node.body])
        go_code = f"""func {func_name}({param_interfaces}) {return_type} {{
        {params}
        {func_body}
        }}
        """
        return go_code

    def visit_FuncCall(self, node):
        func_name = self.visit(node.func_name)
        args = ", ".join([self.visit(arg) for arg in node.args])
        return_cast = ""
        if not isinstance(node.ak_type, types.EmptyTuple):
            return_cast = f".({node.ak_type.go_code()})"
        return f"{func_name}({args}){return_cast}"

    def visit_ReturnStmt(self, node):
        return f"return {self.visit(node.expr)}"

    def visit_PrintStmt(self, node):
        self.imports.add('"fmt"')
        exprs = ",".join([self.visit(expr) for expr in node.args])
        return f"fmt.Println({exprs})"

    def visit_PrintFunc(self, node):
        self.imports.add('"fmt"')
        return "func (x interface{}) interface{} { fmt.Println(x); return nil}"

    def visit_ListIndexExpr(self, node):
        return f"list.At({self.visit(node.var)},{self.visit(node.index_expr)}).({node.ak_type.go_code()})"

    def visit_ListRangeIndexExpr(self, node):
        low = self.visit(node.index_expr.low) if node.index_expr.low else "0"
        if node.index_expr.high:
            high = self.visit(node.index_expr.high)
            return f"list.GetRange({self.visit(node.var)}, {low}, {high})"
        else:
            return f"list.Drop({self.visit(node.var)}, {low})"

    def visit_StringIndexExpr(self, node):
        index_expr = self.visit(node.index_expr)
        return f"{self.visit(node.var)}[{index_expr}:{index_expr}+ types.AkInt(1)]"

    def visit_StringRangeIndexExpr(self, node):
        low = self.visit(node.index_expr.low) if node.index_expr.low else "0"
        if node.index_expr.high:
            high = self.visit(node.index_expr.high)
            return f"{self.visit(node.var)}[{low}:{high}])"
        else:
            return f"{self.visit(node.var)}[{low}:]"

    def visit_ListConsExpr(self, node):
        cons_args_go_code = ",".join([self.visit(arg) for arg in node.cons_args])
        return f"list.Cons({self.visit(node.var)}, {cons_args_go_code})"

    def visit_DictIndexExpr(self, node):
        return f"dict.Get({self.visit(node.var)}, {self.visit(node.index_expr)})"

    def visit_IfExpr(self, node):
        test_expr = self.visit(node.test_expr)
        if_body = "\n".join([self.visit(line) for line in node.if_body])
        if node.else_body:
            else_body = "\n".join([self.visit(line) for line in node.else_body])
            else_stmt = f"""else {{
            {else_body} 
            }}"""
        else:
            else_stmt = ""
        return f"""if {test_expr} {{
            {if_body}
        }} {else_stmt}
        """

    def visit_MatchExpr(self, node):
        if node.test_expr:
            test_expr = self.visit(node.test_expr)
        else:
            test_expr = ""
        case_stmts = ""
        for pattern in node.patterns:
            case_body = "\n".join([self.visit(line) for line in pattern.body])
            if isinstance(pattern, Pattern):
                if node.test_expr:
                    case_stmt = f"\ncase {self.visit(pattern.test_expr)}:\n"
                else:
                    case_stmt = f"\ncase bool({self.visit(pattern.test_expr)}):\n"
            else:
                case_stmt = "\ndefault:\n"
            case_stmts += case_stmt + case_body

        return f"switch {test_expr} {{{case_stmts}}}"

    def visit_StringConcat(self, node):
        return f"{self.visit(node.left)} + {self.visit(node.right)}"

    def visit_RecordDestructDecl(self, node):
        var_inits = "\n".join([self.visit_VarDeclNoInit(var_decl) for var_decl in node.var_decls.values()])
        root_var_decl = self.visit(node.root_var)
        root_name = node.root_var.name
        var_assigns = "\n".join(f"{var} = {root_name}.{var}" for var in node.var_decls.keys())
        res = f"""{var_inits}
        {{
        {root_var_decl}
        {var_assigns}
        }}
        """
        return res

    def visit_ListDestructDecl(self, node):
        self.imports.add('"github.com/aktoro-lang/container/list"')
        var_inits = [self.visit_VarDeclNoInit(var_decl) for var_decl in node.var_decls]
        if node.rest_decl:
            var_inits.append(self.visit_VarDeclNoInit(node.rest_decl))
        var_inits = "\n".join(var_inits)
        root_var_decl = self.visit(node.root_var)
        root_name = node.root_var.name
        var_assigns = [f"{var.name} = list.At({root_name}, types.AkInt({i})).({var.ak_type.go_code()})" for i, var in
                       enumerate(node.var_decls)]
        if node.rest_decl:
            var_assigns.append(
                f"{node.rest_decl.name} = list.Drop({root_name}, types.AkInt({len(node.var_decls)})).({node.rest_decl.ak_type.go_code()})")
        var_assigns = "\n".join(var_assigns)
        res = f"""{var_inits}
        {{
        {root_var_decl}
        {var_assigns}
        }}
        """
        return res
