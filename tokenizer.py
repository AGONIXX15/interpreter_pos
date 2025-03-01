from dataclasses import dataclass
import re
import sys


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int


TOKEN_REGEX = [
    (r"==", "EQUAL"),
    (r"!=", "NOT_EQUAL"),
    (r"<=", "LESS_EQUAL"),
    (r">=", "GREATER_EQUAL"),
    (r"<", "LESS"),
    (r">", "GREATER"),
    (r"\d+(\.\d*)?", "NUMBER"),
    (r"\".*\"", "STRING"),
    (r"'.*'", "STRING"),
    (r"[a-zA-Z_]\w*", "IDENTIFIER"),
    (r"\+", "PLUS"),
    (r"-", "MINUS"),
    (r"\*", "MULTIPLY"),
    (r"/", "DIVIDE"),
    (r"\(", "LPAREN"),
    (r"\)", "RPAREN"),
    (r"=", "ASSIGN"),
    (r"\n", "NEWLINE"),
    (r"\s+", "WHITESPACE"),
]


class Tokenizer:
    __slots__ = ["code", "pos", "line", "column"]

    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1

    def next_token(self):
        while self.pos < len(self.code):
            for pattern, token_type in TOKEN_REGEX:
                regex = re.compile(pattern)
                match = regex.match(self.code, self.pos)
                if match:
                    value = match.group(0)
                    if token_type == "WHITESPACE":
                        self.pos += len(value)
                        self.column += len(value)
                        return self.next_token()
                    elif token_type == "NEWLINE":
                        self.pos += len(value)
                        self.line += 1
                        start_column: int = self.column
                        self.column = 1
                        return Token(token_type, value, self.line-1, start_column)
                    else:
                        start_column: int = self.column
                        self.column += len(value)
                        self.pos += len(value)
                        return Token(token_type, value, self.line, start_column)
            else:
                raise SyntaxError(f"Invalid token at line {
                    self.line}, column {self.column}")
        return Token("EOF", "", self.line, self.column)

    def tokenize(self):
        tokens = []
        while (token := self.next_token()).type != "EOF":
            tokens.append(token)
        return tokens


def read_file(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read()


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("python tokenizer.py <file>")
        sys.exit(1)
    file_path = args[1]
    tokenizer = Tokenizer(read_file(file_path))
    tokens = tokenizer.tokenize()
