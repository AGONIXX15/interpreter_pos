from abc import ABC, abstractmethod


class Stmt(ABC):
    pass


class Expr(ABC):
    @abstractmethod
    def evaluate(self, context: dict):
        pass
