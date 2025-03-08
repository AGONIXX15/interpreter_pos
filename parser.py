from statements import ExpressionStmt
import sys
from tokenizer import Tokenizer, read_file, Token
from lookups import BindingPower
from typing import Callable
from builtins_po import builtin_func, make_builtin_func

from expressions import BinOp, BuiltinFunction, ListArguments, Number, Assignment, \
    Variable, Expr, String, Boolean, UnaryOp, Function, BuiltinFunction, FunctionCall, \
    Return, Null, If, While


bp_lu = {}
nud_lu = {}
led_lu = {}
stmt_lu = {}

global_context = {}
global_functions = {}
keywords = ["return", "func", "if", "elif", "else", "while"]


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

    def advance(self, context):
        self.pos += 1

    def parse_primary_expr(self, context):
        token: Token = self.current_token()

        if token.kind == "NUMBER":
            self.advance(context)
            return Number(float(token.value))
        elif token.kind == "IDENTIFIER":
            # palabra reservada
            # function made by me
            # functions that the user defines
            # check if the identifier is a function
            if token.value in keywords:
                return self.parse_keywords(token.value, context)

            elif builtin_func.get(token.value, None) is not None:
                # from pdb import set_trace; set_trace()
                self.advance(context)  # consume puts
                args = self.parse_list_arguments(context)
                return self.call_function(token.value, args, global_context)
            elif global_functions.get(token.value, None) is not None:
                # from pdb import set_trace; set_trace()
                self.advance(context)
                args = self.parse_list_arguments(context)
                return self.call_function(token.value, args, global_context)

            self.advance(context)
            return Variable(token.value)
        elif token.kind == "STRING":
            self.advance(context)
            return String(token.value[1:-1])
        elif token.kind == "BOOLEAN":
            self.advance(context)
            return Boolean(token.value == "true")
        elif token.kind == "NULL":
            self.advance(context)
            return Null()
        elif token.kind == "LPAREN":
            self.advance(context)
            expr = self.parse_expr(BindingPower.DEFAULT.value, context)
            self.expect("RPAREN")
            return expr
        else:
            raise SyntaxError(f"Unexpected token {token}")

    def parse_keywords(self, name: str, context):
        if name == "func":
            self.advance(context)  # consume "func"
            token = self.current_token()
            global_functions[token.value] = Function(
                token.value, ListArguments([]), [])
            global_functions[token.value] = self.parse_function(context)
            return global_functions[token.value]
        elif name == "return":
            self.advance(context)  # consume "return"
            try:
                return Return(self.parse_expr(BindingPower.DEFAULT.value, context))
            except SyntaxError as e:
                return Return(Null())
        elif name == "if":
            return self.parse_if(context)
        elif name == "while":
            return self.parse_while(context)

    def parse_if(self, context):
        self.advance(context)  # consume "if"
        self.expect("LPAREN")
        conditions = [self.parse_expr(BindingPower.DEFAULT.value, context)]
        self.expect("RPAREN")
        stmts: list[list[Expr]] = [[]]
        else_body = []
        index = 0
        while self.has_more_tokens() and self.current_token().value != "end":
            if self.current_token().value == "else":
                self.advance(context)  # consume "else"
                while self.has_more_tokens() and self.current_token().value != "end":
                    else_body.append(self.parse_stmt(context))
                break
            if self.current_token().value == "elif":
                self.advance(context)
                self.expect("LPAREN")
                conditions.append(
                    self.parse_expr(BindingPower.DEFAULT.value, context))
                self.expect("RPAREN")
                stmts.append([])
                index += 1
            stmts[index].append(self.parse_stmt(context))
        self.advance(context)  # consume "end"
        return If(conditions, stmts, else_body)

    def parse_while(self, context):
        self.advance(context)  # consume while
        self.expect("LPAREN")
        condition = self.parse_expr(BindingPower.DEFAULT.value, context)
        self.expect("RPAREN")
        body = []
        while self.has_more_tokens() and self.current_token().value != "end":
            body.append(self.parse_stmt(context))
        self.advance(context)  # consume "end"
        return While(condition, body)

    def parse_function(self, context):
        token = self.current_token()  # func.name
        name = token.value
        self.advance(context)  # consume name
        args = self.parse_list_arguments(context)  # consume args(a,b,c)
        global_functions[name].args = args
        stmts = []
        while self.has_more_tokens() and self.current_token().value != "end":
            stmt = self.parse_stmt(context)
            global_functions[name].body.append(stmt)
            stmts.append(stmt)

        self.advance(context)
        function = Function(name, args, stmts)
        global_functions[name] = function
        return function

    def call_function(self, name, args, context):
        if name in builtin_func:
            function = BuiltinFunction(
                name, builtin_func[name].function, len(args))
            function.args = args
            return function
        elif name in global_functions:
            # from pdb import set_trace; set_trace()
            function = global_functions[name]
            local_context = {}
            if len(args) != len(function.args):
                raise SyntaxError(
                    f"Function {name} expected {len(function.args)} args, got {len(args)}")
            for var_name, value in zip(function.local_context.keys(), args):
                local_context[var_name] = value

            return FunctionCall(name, args, function.body, {**local_context, **global_functions})
        else:
            raise NameError(f"Function {name} not found")

    def parse_list_arguments(self, context):
        self.expect("LPAREN")
        args = []
        while self.current_token_kind() != "RPAREN":
            args.append(self.parse_expr(BindingPower.DEFAULT.value, context))
            if self.current_token_kind() == "COMMA":
                self.advance(context)
        self.expect("RPAREN")
        return ListArguments(args)

    def parse_binary_expr(self, left: Expr, bp: int, context):
        op_token = self.current_token()
        self.advance(context)
        right = self.parse_expr(bp_lu[op_token.kind], context)
        return BinOp(left, op_token.value, right)

    def parse_stmt(self, context):
        stmt_fn = stmt_lu.get(self.current_token_kind(), None)
        if stmt_fn is not None:
            return stmt_fn()
        # if no statement handler is found, parse an expression
        expression = self.parse_expr(BindingPower.DEFAULT.value, context)
        # expect semicolon at the end of the statement
        self.expect("SEMICOLON")
        return expression

    def parse_expr(self, bp: int, context: dict):
        # from pdb import set_trace; set_trace()
        token_kind = self.current_token_kind()
        nud_fn = nud_lu.get(token_kind, None)
        if nud_fn is None:
            raise SyntaxError(f"Unexpected token {self.current_token()}")
        left = nud_fn(context)
        while self.has_more_tokens() and self.current_token_kind() in bp_lu and bp < bp_lu[self.current_token_kind()]:
            token_kind = self.current_token_kind()
            led_fn = led_lu.get(token_kind, None)
            if led_fn is None:
                raise SyntaxError(f"expected led handler token {
                                  self.current_token()}")
            left = led_fn(left, bp, context)
        return left

    def parse_unary_expr(self, context):
        token = self.current_token()
        self.advance(context)  # consume "-" or "not"
        right = self.parse_expr(BindingPower.UNARY.value, context)
        return UnaryOp(token.value, right)

    def nud(self, kind: str, bp: int, nud_fn: Callable):
        bp_lu[kind] = bp
        nud_lu[kind] = nud_fn

    def led(self, kind: str, bp: int, led_fn: Callable):
        bp_lu[kind] = bp
        led_lu[kind] = led_fn

    def stmt(self, kind: str, stmt_fn: Callable):
        bp_lu[kind] = BindingPower.DEFAULT.value
        stmt_lu[kind] = stmt_fn

    def assignment_led(self, left: Expr, bp: int, context):
        if not isinstance(left, Variable):
            raise SyntaxError(f"Expected variable")
        # from pdb import set_trace; set_trace()
        token = self.current_token()  # assignment
        self.advance(context)
        right = self.parse_expr(bp, context)
        return Assignment(left.name, token.value, right)

    def create_tokens_lookup(self):
        # logical operators
        self.led("AND", BindingPower.LOGICAL.value, self.parse_binary_expr)
        self.led("OR", BindingPower.LOGICAL.value, self.parse_binary_expr)
        self.nud("NOT", BindingPower.UNARY.value, self.parse_unary_expr)

        # relational operators
        self.led("EQUAL", BindingPower.RELATIONAL.value,
                 self.parse_binary_expr)
        self.led("NOT_EQUAL", BindingPower.RELATIONAL.value,
                 self.parse_binary_expr)
        self.led("LESS_EQUAL", BindingPower.RELATIONAL.value,
                 self.parse_binary_expr)
        self.led("GREATER_EQUAL", BindingPower.RELATIONAL.value,
                 self.parse_binary_expr)
        self.led("LESS", BindingPower.RELATIONAL.value, self.parse_binary_expr)
        self.led("GREATER", BindingPower.RELATIONAL.value,
                 self.parse_binary_expr)

        # addition and multiplication and exponential
        self.led("DOUBLE_STAR", BindingPower.EXPONENTIAL.value,
                 self.parse_binary_expr)
        self.led("PLUS", BindingPower.ADDITIVE.value, self.parse_binary_expr)
        self.led("DASH", BindingPower.ADDITIVE.value, self.parse_binary_expr)

        self.led("STAR", BindingPower.MULTIPLICATIVE.value,
                 self.parse_binary_expr)
        self.led("SLASH", BindingPower.MULTIPLICATIVE.value,
                 self.parse_binary_expr)

        self.nud("DASH", BindingPower.UNARY.value, self.parse_unary_expr)
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
        self.nud("NULL", BindingPower.DEFAULT.value, self.parse_primary_expr)

        self.led("ASSIGN", BindingPower.ASSIGNMENT.value, self.assignment_led)
        self.led("PLUS_ASSIGN", BindingPower.ASSIGNMENT.value,
                 self.assignment_led)
        self.led("DASH_ASSIGN", BindingPower.ASSIGNMENT.value,
                 self.assignment_led)
        self.led("STAR_ASSIGN", BindingPower.ASSIGNMENT.value,
                 self.assignment_led)
        self.led("SLASH_ASSIGN", BindingPower.ASSIGNMENT.value,
                 self.assignment_led)

    def expect_error(self, expected_kind: str, error: None | str):
        token: Token = self.current_token()
        if token.kind != expected_kind:
            if error is None:
                error = f"got {token} expected {expected_kind}"
            raise SyntaxError(error)

        self.advance(global_context)

    def expect(self, expected_kind: str):
        self.expect_error(expected_kind, None)

    def parse(self, context: dict):
        self.create_tokens_lookup()
        body: list[ExpressionStmt] = []
        while self.has_more_tokens():
            body.append(self.parse_stmt(context))
        return body


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("python parser.py <file>")
        sys.exit(1)
    file_path = args[1]
    tokenizer = Tokenizer(read_file(file_path))
    tokens: list[Token] = tokenizer.tokenize()
    for token in tokens:
        print(token)
    parser = Parser(tokens)
    global_context: dict = {}
    ast: list[ExpressionStmt] = parser.parse(global_context)
    print(global_context)
    for stmt in ast:
        print(stmt)
    global_context: dict = {}
    ast: list[ExpressionStmt] = parser.parse(global_context)
    print(global_context)
    for stmt in ast:
        print(stmt)
    for stmt in ast:
        print(stmt)
