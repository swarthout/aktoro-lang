from pathlib import Path
from lark import Lark
from aktoro.code_gen import CodeGenVisitor
from aktoro.type_checker import TypeCheckVisitor
from aktoro.parser import Parser
import os

current_dir = os.path.dirname(__file__)

AK_GRAMMAR_FILENAME: str = Path(current_dir) / "aktoro.g"

with open(AK_GRAMMAR_FILENAME) as f:
    AK_GRAMMAR = Lark(f, parser="lalr", start="program")


def compile_ak(ak_source):
    parse_tree = AK_GRAMMAR.parse(ak_source)
    ast = Parser().transform(parse_tree)
    check = TypeCheckVisitor()
    checked_ast = check.visit(ast)
    code_gen = CodeGenVisitor()
    go_code = code_gen.visit(checked_ast)
    return go_code
