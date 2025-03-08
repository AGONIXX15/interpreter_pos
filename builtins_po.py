from expressions import BuiltinFunction
from typing import Callable
import re
builtin_func = {}


def make_builtin_func(name: str, function: Callable, args_count: int | None = None):
    builtin_func[name] = BuiltinFunction(name, function, args_count)


def read_input(message: str):
    message = input(message)
    search = [(r"\d+(\.\d*)?", "number"), (r"\w+", "name")]
    for pattern, name in search:
        if re.match(pattern, message):
            if name == "name":
                return message
            elif name == "number":
                return float(message)

def print_it(*args):
    for arg in args:
        if arg is None:
            print("null", end=" ")
        if arg is True:
            print("true", end=" ")
        if arg is False:
            print("false", end=" ")
        if isinstance(arg, str):
            print(arg, end=" ")
        if isinstance(arg, float):
            print(arg, end=" ")
    print()


def my_sum(*args):
    total = 0
    for n in args:
        total += n
    return float(total)


def make_builtin_funcs():
    make_builtin_func("puts", print_it, None)
    make_builtin_func("input", read_input, 1)
    make_builtin_func("sum", my_sum, None)


make_builtin_funcs()
