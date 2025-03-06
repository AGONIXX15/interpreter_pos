from typing import Any, Self, Callable
from ast import Expr


class Number(Expr):
    __slots__ = ["value"]

    def __init__(self, value) -> None:
        self.value = value

    def evaluate(self, context: dict):
        return self.value

    def __repr__(self):
        return f"Number({self.value})"


class String(Expr):
    __slots__ = ["value"]

    def __init__(self, value: str) -> None:
        self.value: str = value

    def evaluate(self, context: dict):
        return self.value

    def __repr__(self) -> str:
        return f"String({self.value})"


class Variable(Expr):
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, context):
        if self.name in context:
            return context[self.name]
        raise NameError(f"Var {self.name} not found")

    def __repr__(self):
        return f"Variable('{self.name}')"


class Boolean(Expr):
    __slots__ = ["value"]

    def __init__(self, value: bool):
        self.value: bool = value

    def evaluate(self, context):
        return self.value

    def __repr__(self):
        return f"Boolean({self.value})"


class ListArguments(Expr):
    __slots__ = ["args"]

    def __init__(self, args: list[Expr]):
        self.args = args

    def evaluate(self, context):
        return [arg.evaluate(context) for arg in self.args]

    def __len__(self):
        return len(self.args)

    def __next__(self):
        return next(self.args)

    def __iter__(self):
        return iter(self.args)

    def __repr__(self) -> str:
        return f"ListArguments({self.args})"


class Function(Expr):
    __slots__ = ["name", "args", "body", "local_context"]

    def __init__(self, name: str, args: ListArguments, body: list[Expr]):
        self.name: str = name
        self.args: ListArguments = args
        self.body = body
        self.local_context = {x.name: None for x in args}

    def evaluate(self, context):
        pass

    def __repr__(self) -> str:
        return f"Function(name={self.name}, args={self.args}, body={self.body})"


class FunctionCall(Expr):
    __slots__ = ["name", "args", "body", "local_context"]

    def __init__(self, name: str, args: ListArguments, body: list[Expr], local_context):
        self.name: str = name
        self.args: ListArguments = args
        self.body: list[Expr] = body
        self.local_context = local_context

    def evaluate(self, context):
        self.local_context = {k: v.evaluate(
            context) for k, v in self.local_context.items()}
        self.local_context = self.local_context | context
        for expr in self.body:
            expr.evaluate(self.local_context)

    def __repr__(self) -> str:
        return f"FunctionCall(name={self.name},{self.local_context} ,args={self.args}, body={self.body})"


class BuiltinFunction(Expr):
    __slots__ = ["value", "function", "args_count", "args"]

    def __init__(self, value: str, function: Callable, args_count: int | None = None):
        self.value: str = value
        self.function = function
        self.args_count = args_count
        self.args = []

    def evaluate(self, context):
        copy_args = self.args.evaluate(context)
        if self.args_count is not None and len(copy_args) != self.args_count:
            raise ValueError("invalid number of arguments")
        return self.function(*copy_args)

    def __repr__(self) -> str:
        return f"BuiltinFunction(value={self.value},function={self.function}, args={self.args})"


class Assignment(Expr):
    def __init__(self, name: str, op: str, value: Expr):
        self.name = name
        self.op = op
        self.value: Expr = value

    def evaluate(self, context):
        if self.op == "=":
            context[self.name]: Any = self.value.evaluate(context)
        elif self.op == "+=":
            context[self.name] += self.value.evaluate(context)
        elif self.op == "-=":
            context[self.name] -= self.value.evaluate(context)
        elif self.op == "*=":
            context[self.name] *= self.value.evaluate(context)
        elif self.op == "/=":
            context[self.name] /= self.value.evaluate(context)
        else:
            return context[self.name]

    def __repr__(self) -> str:
        return f"Assignment('{self.name}',op='{self.op}', {repr(self.value)})"


class UnaryOp(Expr):
    __slots__ = ["op", "expr"]

    def __init__(self, op: str, expr: Expr):
        self.op = op
        self.expr: Expr = expr

    def evaluate(self, context):
        if self.op == "-":
            return -self.expr.evaluate(context)
        elif self.op == "not":
            return not self.expr.evaluate(context)
        else:
            raise SyntaxError("dont know the unary operator")

    def __repr__(self) -> str:
        return f"UnaryOp(op=\"{self.op}\", expr={self.expr})"


class BinOp(Expr):
    __slots__ = ["left", "op", "right"]

    def __init__(self, left: Expr, op: str, right: Expr) -> Self:
        self.left = left
        self.op = op
        self.right = right

    def evaluate(self, context):
        left_val = self.left.evaluate(context)
        right_val = self.right.evaluate(context)
        if self.op == "+":
            return left_val + right_val
        elif self.op == "-":
            return left_val - right_val
        elif self.op == "**":
            return left_val ** right_val
        elif self.op == "*":
            return left_val * right_val
        elif self.op == "/":
            # need to see the condition for division by zero
            return left_val / right_val
        elif self.op == "and":
            return left_val and right_val
        elif self.op == "or":
            return left_val or right_val
        elif self.op == "==":
            return left_val == right_val
        elif self.op == "!=":
            return left_val != right_val
        elif self.op == ">":
            return left_val > right_val
        elif self.op == ">=":
            return left_val >= right_val
        elif self.op == "<":
            return left_val < right_val
        elif self.op == "<=":
            return left_val <= right_val
        else:
            raise SyntaxError("dont know the operator")

    def __repr__(self) -> str:
        return f"BinOp(left={self.left}, op=\"{self.op}\", right={self.right})"


if __name__ == "__main__":
    expression = BinOp(Number(3), "+", BinOp(Number(5), "-", Number(2)))
