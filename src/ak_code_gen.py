from collections import namedtuple
import textwrap
from ak_ast import *
from ak_types import *
from ak_parse import snake_to_camel


class CodeGenVisitor(NodeVisitor):

    def __init__(self):
        super(CodeGenVisitor, self).__init__()

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

        go_body = textwrap.dedent("""
                    package main
                    import (
                    "fmt"
                    )
                    {record_decls}
                    func main() {{
                    {main_code}
                    }}

                    """)
        return go_body.format(main_code=textwrap.indent(main_go_code, "\t"), record_decls=record_decl_go_code)

    def visit_VarDecl(self, node):
        node_name = self.visit_VarUsage(node)
        return f"{node_name} := {self.visit(node.expr)}"

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
        return node.value

    def visit_ListLiteral(self, node):
        elem_type_go_code = node.ak_type.elem_type.go_code()
        elems = [self.visit(elem) for elem in node.values]
        elem_go_code = ", ".join(elems)
        return f"[]{elem_type_go_code}{{{elem_go_code}}}"

    def visit_DictLiteral(self, node):
        pass

    def visit_RecordLiteral(self, node):
        fields = [f"{name}: {self.visit(expr)}" for name, expr in node.fields.items()]
        fields = ",\n".join([textwrap.indent(f, "\t") for f in fields])
        record_type = node.ak_type.go_code()
        go_code = f"{record_type}{{\n" + textwrap.indent(fields, "\t") + textwrap.dedent("}")
        return go_code

    def visit_BinaryOpExpr(self, node):
        return f"{self.visit(node.left)} {node.op} {self.visit(node.right)}"

    def visit_ParamDecl(self, node):
        return f"{snake_to_camel(node.name)} {node.ak_type.go_code()}"

    def visit_FuncDef(self, node):
        params = [self.visit(param) for param in node.params.values()]
        params = ", ".join(params)
        func_body = "\n".join([self.visit(line) for line in node.body])
        return_type = node.return_type.go_code()
        go_code = f"""func ({params}) {return_type} {{
        {func_body}
        }}
        """
        return go_code

    def visit_FuncCall(self, node):
        func_name = self.visit(node.func_name)
        args = ", ".join([self.visit(arg) for arg in node.args])
        return f"{func_name}({args})"

    def visit_ReturnExpr(self, node):
        return f"return {self.visit(node.expr)}"

    def visit_PrintStmt(self, node):
        exprs = ",".join([self.visit(expr) for expr in node.exprs])
        return f"fmt.Println({exprs})"
