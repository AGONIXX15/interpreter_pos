from Ast import Expr, Stmt


class BlockStmt:
    __slots__ = ["body"]

    def __init__(self, body: list[Stmt] | None = None):
        self.body: list[Stmt] = [] if body is None else body

    def __repr__(self):
        return f"BlockStmt({self.body})"


class ExpressionStmt:
    __slots__ = ["expression"]

    def __init__(self, expr: Expr):
        self.expression: Expr = expr

    def evaluate(self, context: dict):
        return self.expression.evaluate(context)

    def __repr__(self):
        return f"ExpressionStmt({self.expression})"
