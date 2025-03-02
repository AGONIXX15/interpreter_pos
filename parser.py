import sys
from tokenizer import Tokenizer, read_file, Token

from expressions import BinOp, Number, Assignment, Variable, Expr, String


class Parser:
    __slots__ = ["tokens", "pos"]

    def __init__(self, tokens: list[Token]):
        self.tokens: list[Token] = tokens
        self.pos: int = 0

    def current_token(self):
        return self.tokens[self.pos]

    def has_more_tokens(self):
        return (self.pos < len(self.tokens) and
                self.current_token().kind != "EOF")

    def advance(self):
        self.pos += 1

    def parse_factor(self):
        token: Token = self.current_token()

        if token.kind == "NUMBER":
            self.advance()
            return Number(float(token.value))
        elif token.kind == "IDENTIFIER":
            self.advance()
            return Variable(token.value)
        elif token.kind == "STRING":
            self.advance()
            return String(token.value)
        elif token.kind == "LPAREN":
            # consume "("
            self.advance()
            expr = self.parse_expr()
            if self.has_more_tokens() and self.current_token().kind == "RPAREN":
                # consume ")"
                self.advance()
                return expr
            else:
                raise SyntaxError("u dont have a close parenthesis")
        else:
            raise SyntaxError("not known that token")

    def parse_term(self):
        expr: Expr = self.parse_factor()
        if self.has_more_tokens() and self.current_token().value in ("*", "/"):
            op: str = self.current_token().value
            self.advance()
            expr = BinOp(expr, op, self.parse_factor())
        # if self.has_more_tokens() and self.current_token().value in ("+", "-"):
        #     op: str = self.current_token().value
        #     self.advance()
        #     expr = BinOp(expr, op, self.parse_factor())

        return expr

    def parse_expr(self):
        expr: Expr = self.parse_term()
        print(expr)
        if self.has_more_tokens() and self.current_token().value in ("+", "-"):
            op: str = self.current_token().value
            self.advance() # consume "+|-"
            expr = BinOp(expr, op, self.parse_term())
        return expr

    def parse_assignment(self):
        token: Token = self.current_token()
        if token.kind == "IDENTIFIER":
            name: str = token.value
            self.advance()  # consume the identifier
            if self.has_more_tokens() and self.current_token().kind == "ASSIGN":
                self.advance()  # consume the "="
                # value of the variable
                value: Expr = self.parse_expr()
                return Assignment(name, value)
        return self.parse_expr()

    def parse(self):
        statements = []
        while self.has_more_tokens():
            stmt = self.parse_assignment()
            statements.append(stmt)
            while self.has_more_tokens() and self.current_token().kind == "NEWLINE":
                self.advance()
        return statements


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("python parser.py <file>")
        sys.exit(1)
    file_path = args[1]
    tokenizer = Tokenizer(read_file(file_path))
    tokens = tokenizer.tokenize()
    # for token in tokens:
    #     print(token)
    parser = Parser(tokens)
    ast = parser.parse()
    global_context = {}
    # for stmt in ast:
    #     result = stmt.evaluate(global_context)
    #     print(f"{stmt} -> {result}")

    # print("this is the vars of my program")
    # for name, value in global_context.items():
    #     print(f"{name} = {value}")
