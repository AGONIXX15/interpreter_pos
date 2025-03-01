import sys

# study about parsers


class Parser:
    def __init__(self, tokens: list) -> None:
        self.tokens = tokens


if __name__ == "__main__":
    from tokenizer import Tokenizer, read_file
    args = sys.argv
    if len(args) < 2:
        print("python tokenizer.py <file>")
        sys.exit(1)
    file_path = args[1]
    tokenizer = Tokenizer(read_file(file_path))
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)
