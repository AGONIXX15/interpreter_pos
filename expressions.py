from abc import abstractmethod, ABC
from typing import Self


class Expr(ABC):
    @abstractmethod
    def evaluate(self, context):
        pass


class Number(Expr):
    __slots__ = ["value"]

    def __init__(self, value) -> None:
        self.value = value

    def evaluate(self, context):
        return self.value

    def __repr__(self):
        return f"Number({self.value})"


class String(Expr):
    __slots__ = ["value"]

    def __init__(self, value) -> None:
        self.value = value

    def evaluate(self, context):
        return self.value[1:-1]

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


class Assignment(Expr):
    def __init__(self, name: str, value: Expr):
        self.name = name
        self.value = value

    def evaluate(self, context):
        context[self.name] = self.value.evaluate(context)
        return context[self.name]

    def __repr__(self) -> str:
        return f"Assignment('{self.name}', {repr(self.value)})"


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
        elif self.op == "*":
            return left_val * right_val
        elif self.op == "/":
            # need to see the condition for division by zero
            return left_val / right_val
        else:
            raise SyntaxError("dont know the operator")

    def __repr__(self) -> str:
        return f"BinOp(left={self.left}, op={self.op}, right={self.right})"


if __name__ == "__main__":
    # 3 + 5 - 2
    expression = BinOp(Number(3), "+", BinOp(Number(5), "-", Number(2)))
