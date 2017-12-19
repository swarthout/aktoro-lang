from lark import Lark
from code_gen import CodeGen
import argparse
import os.path
from io import open

__path__ = os.path.dirname(__file__)

othello_grammar_filename = os.path.join(__path__, "othello.g")

with open(othello_grammar_filename) as f:
    othello_parser = Lark(f, parser="lalr", start="program")

arg_parser = argparse.ArgumentParser(description="Othello Programming Language")
arg_parser.add_argument('filename', type=str, help="othello filename")

args = arg_parser.parse_args()

input_filename = os.path.join(__path__, args.filename)
with open(input_filename) as ol:
    program = ol.read()

parse_tree = othello_parser.parse(program)

print(parse_tree.pretty())

go_code = CodeGen().transform(parse_tree)

print(go_code)
