import inspect
from typing import *

__all__ = ["INDENT", "include", "get_main_source_file", "method_to_function_source"]

INDENT = 4

include = _IncludeDecorator  # alias for Include class


def _indent(line: str, num_tabs: int = 1) -> str:
    return " " * INDENT * num_tabs + line


def _dedent(line: str, num_tabs: int = 1) -> str:
    return line[num_tabs * INDENT :]


class _IncludeDecorator:
    """_IncludeDecorator: the decorator class that annotate Jar methods as included functions in the main function.
    In Jar.entrypoint the method can still be called by original name. But the original unwrapped method is preseved as method `_original_<method_name>`.
    """

    def __init__(self, method):
        self.method = method

    def __get__(self, instance, owner) -> Callable:
        self.instance = instance
        return self.__call__

    def __call__(self, *args, **kwargs) -> Any:
        key = self.method.__name__
        if key not in self.instance._helper_registry:
            val = f"_original_{key}"
            self.instance._helper_registry[key] = val
            setattr(self.instance, val, self.method)
        return self.method(self.instance, *args, **kwargs)


def get_main_source_file(src: str, argspec: NamedTuple) -> str:
    ln = []
    ln.append(src)
    ln.append("if __name__ == '__main__':")
    ln.append(_indent("import argparse"))
    ln.append(_indent("parser = argparse.ArgumentParser()"))
    for arg, typ in argspec.annotations.items():
        if arg == "self":
            continue
        if typ in (list, tuple):
            nargs = "+"
            typ = typ.__args__[0]
        else:
            nargs = "1"
        ln.append(
            _indent(
                f"parser.add_argument('--{arg}', type={typ.__name__}, nargs={nargs})"
            )
        )
    ln.append(_indent("kwargs = vars(parser.parse_args())"))
    ln.append(_indent("entrypoint(**kwargs)"))

    return "\n".join(ln)


def method_to_function_source(method: Callable) -> str:
    lines = inspect.getsource(method).split("\n")
    argspec = inspect.getfullargspec(method)
    first_non_self_arg = 0
    for arg in argspec.args:
        if arg == "self":
            first_non_self_arg += 1
            continue
        assert (
            arg in argspec.annotations
        ), f"Arg {arg} is not annotated. All args should be annotated kwargs."
    source = [
        f"def {method.__name__}({', '.join(argspec.args[first_non_self_arg:])}):"
    ]  # do not include `self`
    for ln in lines[1:]:
        source.append(_dedent(ln))

    return "\n".join(source)
