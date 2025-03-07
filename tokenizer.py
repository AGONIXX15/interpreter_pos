from dataclasses import dataclass
import re
import sys


@dataclass
class Token:
    kind: str
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
    (r"and", "AND"),
    (r"or", "OR"),
    (r"not", "NOT"),
    (r"\d+\.{2}\d+", "DOUBLE_DOT"),
    (r"\d+(\.\d*)?", "NUMBER"),
    (r"true|false", "BOOLEAN"),
    (r"\".*?\"", "STRING"),
    (r"'.*?'", "STRING"),
    (r",", "COMMA"),
    (r"null", "NULL"),
    (r"[a-zA-Z_]\w*", "IDENTIFIER"),
    (r"\+=", "PLUS_ASSIGN"),
    (r"-=", "DASH_ASSIGN"),
    (r"\*=", "STAR_ASSIGN"),
    (r"/=", "SLASH_ASSIGN"),
    (r"=", "ASSIGN"),
    (r"\*\*", "DOUBLE_STAR"),
    (r"\+", "PLUS"),
    (r"-", "DASH"),
    (r"\*", "STAR"),
    (r"/", "SLASH"),
    (r"\(", "LPAREN"),
    (r"\)", "RPAREN"),
    (r";", "SEMICOLON"),
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
                        return self.next_token()
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
        while (token := self.next_token()).kind != "EOF":
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
    print(tokens)
    for token in tokens:
        print(token)
