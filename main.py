#!/usr/bin/env python
import sys
from tokenizer import Tokenizer, read_file
from parser import Parser
import argparse

# create a parser
# type of parser recursive descent


def run_file(files: list[str], options=None):
    if options is None:
        options = {}
    global_context = {}
    for file_name in files:
        tokenizer = Tokenizer(read_file(file_name))
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse(global_context)
        for stmt in ast:
            stmt.evaluate(global_context)
        if "debug" in options:
            for token in tokens:
                print(token)
            for stmt in ast:
                print(stmt)
            print(global_context)
            print(ast)

            print("this is the vars of my program")
            for name, value in global_context.items():
                print(f"{name} = {value}")


def run_interpreter(options=None):
    if options is None:
        options = {}
    global_context = {}
    while True:
        input_text = input("$$ ")
        tokenizer = Tokenizer(input_text)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse(global_context)
        for stmt in ast:
            stmt.evaluate(global_context)
        if "debug" in options:
            for token in tokens:
                print(token)

            print(global_context)

            print("this is the vars of my program")
            for name, value in global_context.items():
                print(f"{name} = {value}")


def main():
    parse = argparse.ArgumentParser(prog="pos")
    parse.add_argument("filename", nargs="*")
    parse.add_argument("-d", "--debug", default=False,
                       action=argparse.BooleanOptionalAction)
    args = parse.parse_args()
    options = {}
    if args.debug:
        options["debug"] = True
    if not args.filename:
        run_interpreter(options)
        sys.exit(1)
    run_file(args.filename, options)


if __name__ == "__main__":
    main()
