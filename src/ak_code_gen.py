from collections import namedtuple
import textwrap
from ak_ast import *
from ak_types import *
from ak_parse import snake_to_camel


class CodeGenVisitor(NodeVisitor):

    def __init__(self):
        super(CodeGenVisitor, self).__init__()
        self.imports = set()

    def visit(self, node):
        '''
        Execute a method of the form visit_NodeName(node) where
        NodeName is the name of the class of a particular node.
        '''
        if node:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            return visitor(node)
        else:
            return None

    def visit_Program(self, node):

        record_decls = []
        main_statements = []
        for line in node.statements:
            if isinstance(line, RecordDecl):
                record_decls.append(line)
            elif line is not None:
                main_statements.append(line)
        main_go_code = "\n".join([self.visit(s) for s in main_statements])
        record_decl_go_code = "\n".join([self.visit(r) for r in record_decls])
        imports_go_code = "\n".join(list(self.imports))

        go_body = textwrap.dedent("""
                    package main
                    import (
                    {imports}
                    )
                    {record_decls}
                    func main() {{
                    {main_code}
                    }}

                    """)
        return go_body.format(main_code=textwrap.indent(main_go_code, "\t"), record_decls=record_decl_go_code,
                              imports=imports_go_code)

    def visit_VarDecl(self, node):
        node_name = self.visit_VarUsage(node)
        return f"{node_name} := {self.visit(node.expr)}"

    def visit_VarIfAssign(self, node):
        var_decl = self.visit_VarDeclNoInit(node)

        return var_decl + "\n" + self.visit(node.expr)

    def visit_VarDeclNoInit(self, node):
        node_name = self.visit_VarUsage(node)
        return f"var {node_name} {node.ak_type.go_code()}"

    def visit_VarAssignMut(self, node):
        node_name = self.visit_VarUsage(node)
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

    def visit_VarUsage(self, node):
        snake_names = [snake_to_camel(name) for name in node.name.split(".")]
        go_code = ".".join(snake_names)
        return go_code

    def visit_PrimitiveLiteral(self, node):
        self.imports.add('"github.com/aktoro-lang/types"')
        literal_type = node.ak_type.name
        if literal_type == "string":
            return f"types.AkString({node.value})"
        elif literal_type == "int":
            return f"types.AkInt({node.value})"
        elif literal_type == "float":
            return f"types.AkFloat({node.value})"
        elif literal_type == "bool":
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

    def visit_BinaryOpExpr(self, node):
        return f"{self.visit(node.left)} {node.op} {self.visit(node.right)}"

    def visit_ParamDecl(self, node):
        return f"{snake_to_camel(node.name)} {node.ak_type.go_code()}"

    def visit_FuncDef(self, node):
        params = []
        for param in node.params.values():
            params.append(f"{param.name} {param.ak_type.go_code()}")
        params = "\n".join(params)
        return_type = node.return_type.go_code()
        func_body = "\n".join([self.visit(line) for line in node.body])
        go_code = f"""func({params}) {return_type} {{
        {func_body}
        }}
        """
        return go_code

    def visit_FuncCall(self, node):
        func_name = self.visit(node.func_name)
        args = ", ".join([self.visit(arg) for arg in node.args])
        return f"{func_name}({args})"

    def visit_ReturnStmt(self, node):
        return f"return {self.visit(node.expr)}"

    def visit_PrintStmt(self, node):
        self.imports.add('"fmt"')
        exprs = ",".join([self.visit(expr) for expr in node.exprs])
        return f"fmt.Println({exprs})"

    def visit_ListIndexExpr(self, node):
        if isinstance(node.index_expr, RangeIndex):
            return self.visit_ListRangeIndexExpr(node)
        else:
            return f"list.At({self.visit(node.var)},{self.visit(node.index_expr)}).({node.ak_type.go_code()})"

    def visit_ListRangeIndexExpr(self, node):
        low = self.visit(node.index_expr.low) if node.index_expr.low else "0"
        if node.index_expr.high:
            high = self.visit(node.index_expr.high)
            return f"list.GetRange({self.visit(node.var)}, {low}, {high})"
        else:
            return f"list.Drop({self.visit(node.var)}, {low})"

    def visit_ListConsExpr(self, node):
        cons_args_go_code = ",".join([self.visit(arg) for arg in node.cons_args])
        return f"list.Cons({self.visit(node.var)}, {cons_args_go_code})"

    def visit_DictIndexExpr(self, node):
        return f"dict.Get({self.visit(node.var)}, {self.visit(node.index_expr)})"

    def visit_IfExpr(self, node):
        test_expr = self.visit(node.test_expr)
        if_body = "\n".join([self.visit(line) for line in node.if_body])
        if node.else_body:
            else_body = "\n".join([self.visit(line) for line in node.if_body])
            else_stmt = f"""else {{
            {else_body} 
            }}"""
        else:
            else_stmt = ""
        return f"""if {test_expr} {{
            {if_body}
        }} {else_stmt}
        """
