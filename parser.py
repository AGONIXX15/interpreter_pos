import sys
from tokenizer import Tokenizer, read_file, Token
from lookups import BindingPower
from typing import Callable

from expressions import BinOp, Number, Assignment, Variable, Expr, String, Boolean
from statements import ExpressionStmt


bp_lu = {}
nud_lu = {}
led_lu = {}
stmt_lu = {}


class Parser:
    __slots__ = ["tokens", "pos"]

    def __init__(self, tokens: list[Token]):
        self.tokens: list[Token] = tokens
        self.pos: int = 0

    def current_token(self):
        return self.tokens[self.pos]

    def current_token_kind(self):
        return self.current_token().kind

    def has_more_tokens(self):
        return (self.pos < len(self.tokens) and
                self.current_token().kind != "EOF")

    def advance(self):
        self.pos += 1

    def parse_primary_expr(self):
        token: Token = self.current_token()
        print(token.kind)

        if token.kind == "NUMBER":
            self.advance()
            return Number(float(token.value))
        elif token.kind == "IDENTIFIER":
            self.advance()
            return Variable(token.value)
        elif token.kind == "STRING":
            self.advance()
            return String(token.value[1:-1])
        elif token.kind == "BOOLEAN":
            self.advance()
            return Boolean(token.value == "true")
        elif token.kind == "LPAREN":
            self.advance()
            expr = self.parse_expr(BindingPower.DEFAULT.value)
            if self.current_token_kind() != "RPAREN":
                raise SyntaxError(f"Expected close paren )")
            self.advance()  # consume ")"
            return expr
        else:
            raise SyntaxError(f"Unexpected token {token}")

    def parse_binary_expr(self, left: Expr, bp: int):
        op_token = self.current_token()
        self.advance()
        right = self.parse_expr(bp_lu[op_token.kind])
        return BinOp(left, op_token.value, right)

    def parse_stmt(self):
        stmt_fn = stmt_lu.get(self.current_token_kind(), None)
        if stmt_fn is not None:
            return stmt_fn()
        # if no statement handler is found, parse an expression
        expression = self.parse_expr(BindingPower.DEFAULT.value)
        # expect semicolon at the end of the statement
        self.expect("SEMICOLON")
        return ExpressionStmt(expression)

    def parse_expr(self, bp: int):
        token_kind = self.current_token_kind()
        nud_fn = nud_lu.get(token_kind, None)
        if nud_fn is None:
            raise SyntaxError(f"Unexpected token {self.current_token()}")
        left = nud_fn()
        while self.current_token_kind() in bp_lu and bp < bp_lu[self.current_token_kind()]:
            token_kind = self.current_token_kind()
            led_fn = led_lu.get(token_kind, None)
            if led_fn is None:
                raise SyntaxError(f"expected led handler token {
                                  self.current_token()}")
            left = led_fn(left, bp)
        return left

    def nud(self, kind: str, bp: int, nud_fn: Callable):
        bp_lu[kind] = bp
        nud_lu[kind] = nud_fn

    def led(self, kind: str, bp: int, led_fn: Callable):
        bp_lu[kind] = bp
        led_lu[kind] = led_fn

    def stmt(self, kind: str, stmt_fn: Callable):
        bp_lu[kind] = BindingPower.DEFAULT.value
        stmt_lu[kind] = stmt_fn

    def assignment_led(self, left: Expr, bp: int):
        print(f"processing assignment {left}")
        if not isinstance(left, Variable):
            raise SyntaxError(f"Expected variable")
        # from pdb import set_trace; set_trace()
        self.advance()
        right = self.parse_expr(bp)
        return Assignment(left.name, right)

    def create_tokens_lookup(self):
        # logical operators
        self.led("AND", BindingPower.LOGICAL.value, self.parse_binary_expr)
        self.led("OR", BindingPower.LOGICAL.value, self.parse_binary_expr)

        # relational operators
        self.led("EQUAL", BindingPower.RELATIONAL.value,
                 self.parse_binary_expr)
        self.led("NOT_EQUAL", BindingPower.RELATIONAL.value, self.parse_binary_expr)
        self.led("LESS_EQUAL", BindingPower.RELATIONAL.value, self.parse_binary_expr)
        self.led("GREATER_EQUAL", BindingPower.RELATIONAL.value, self.parse_binary_expr)
        self.led("LESS", BindingPower.RELATIONAL.value, self.parse_binary_expr)
        self.led("GREATER", BindingPower.RELATIONAL.value, self.parse_binary_expr)

        # addition and multiplication
        self.led("PLUS", BindingPower.ADDITIVE.value, self.parse_binary_expr)
        self.led("DASH", BindingPower.ADDITIVE.value, self.parse_binary_expr)

        self.led("STAR", BindingPower.MULTIPLICATIVE.value,
                 self.parse_binary_expr)
        self.led("SLASH", BindingPower.MULTIPLICATIVE.value,
                 self.parse_binary_expr)

        # primary expressions
        self.nud("NUMBER", BindingPower.PRIMARY.value, self.parse_primary_expr)
        self.nud("STRING", BindingPower.PRIMARY.value, self.parse_primary_expr)
        self.nud("IDENTIFIER", BindingPower.PRIMARY.value,
                 self.parse_primary_expr)
        self.nud("BOOLEAN", BindingPower.PRIMARY.value,
                 self.parse_primary_expr)
        # delimiters
        self.nud("LPAREN", BindingPower.DEFAULT.value, self.parse_primary_expr)
        self.nud("RPAREN", BindingPower.DEFAULT.value, self.advance)

        self.led("ASSIGN", BindingPower.ASSIGNMENT.value, self.assignment_led)

    def expect_error(self, expected_kind: str, error: None | str):
        token = self.current_token()
        if token.kind != expected_kind:
            if error is None:
                error = f"got {token} expected {expected_kind}"
            raise SyntaxError(error)

        self.advance()

    def expect(self, expected_kind: str):
        self.expect_error(expected_kind, None)

    def parse(self):
        self.create_tokens_lookup()
        body: list[ExpressionStmt] = []
        while self.has_more_tokens():
            body.append(self.parse_stmt())
        return body


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("python parser.py <file>")
        sys.exit(1)
    file_path = args[1]
    tokenizer = Tokenizer(read_file(file_path))
    tokens = tokenizer.tokenize()
    for token in tokens:
        print(token)
    parser = Parser(tokens)
    ast = parser.parse()
    global_context = {}
    print(ast)
    for stmt in ast:
        if stmt is not None:
            result = stmt.evaluate(global_context)
            print(f"{stmt} -> {result}")

    print("this is the vars of my program")
    for name, value in global_context.items():
        print(f"{name} = {value}")
