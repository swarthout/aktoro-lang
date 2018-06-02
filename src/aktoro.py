#!/usr/bin/env python3
from lark import Lark
from ak_code_gen import CodeGenVisitor
from ak_check import TypeCheckVisitor
from ak_parse import Parser
import argparse
import os.path
import subprocess
import time
from io import open

__path__ = os.path.dirname(__file__)

cli = argparse.ArgumentParser()
subparsers = cli.add_subparsers(dest="subcommand")

AK_GRAMMAR_FILENAME = os.path.join(__path__, "aktoro.g")

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


def sub_command(args=None, parent=subparsers):
    if args is None:
        args = []

    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)

    return decorator


def argument(*name_or_flags, **kwargs):
    return [*name_or_flags], kwargs


@sub_command([argument('filename', type=str, help="filename"),
              argument('-o', type=str, help="output")])
def build(args):
    input_filename = os.path.join(__path__, args.filename)
    with open(input_filename) as ol:
        program = ol.read()

    generated = compile_ak(program)

    input_filename_no_extension = input_filename.split(".ak", 1)[0]
    input_path = input_filename_no_extension.split("/")
    input_path = "/".join(input_path[:len(input_path) - 1])
    temp_go_filename = str(input_filename_no_extension) + \
                       "_aktoro_generated" + ".go"
    with open(temp_go_filename, "w") as go_file:
        go_file.write(generated)
    build_str = f"cd {input_path} && go build"
    if args.o:
        build_str += f" -o {args.o}"
    subprocess.check_output(build_str, shell=True, )
    os.remove(temp_go_filename)


@sub_command([argument('filename', type=str, help="filename")])
def run(args):
    input_filename = os.path.join(__path__, args.filename)
    with open(input_filename) as ak:
        program = ak.read()

    generated = compile_ak(program)
    input_filename_no_extension = input_filename.split(".ak", 1)[0]
    temp_go_filename = str(input_filename_no_extension) + \
                       "_aktoro_generated" + ".go"
    with open(temp_go_filename, "w") as go_file:
        go_file.write(generated)
    output = subprocess.check_output(f"go run {temp_go_filename}", shell=True)
    output = output.decode("utf-8")
    os.remove(temp_go_filename)
    print(output)


@sub_command([argument('filename', type=str, help="filename")])
def parse(args):
    input_filename = os.path.join(__path__, args.filename)
    with open(input_filename) as ol:
        program = ol.read()

    parse_tree = AK_GRAMMAR.parse(program)
    print(parse_tree.pretty())


@sub_command([argument('filename', type=str, help="filename")])
def generate(args):
    input_filename = os.path.join(__path__, args.filename)
    with open(input_filename) as ak:
        program = ak.read()

    generated = compile_ak(program)
    print(generated)


if __name__ == "__main__":
    args = cli.parse_args()
    if args.subcommand is None:
        cli.print_help()
    else:
        args.func(args)
