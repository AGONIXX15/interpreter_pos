#!/usr/bin/env python
import sys
from tokenizer import Tokenizer, read_file

# create a parser
# type of parser recursive descent


def main():
    args = sys.argv
    if len(args) < 2:
        print("python tokenizer.py <file>")
        sys.exit(1)
    file_path = args[1]
    tokenizer = Tokenizer(read_file(file_path))
    tokens = tokenizer.tokenize()
    for token in tokens:
        print(token)


if __name__ == "__main__":
    main()
