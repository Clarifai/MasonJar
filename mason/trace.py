import inspect
from typing import *

__all__ = ["INDENT", "include", "get_main_source_file", "get_function_source"]

INDENT = 4

_fm = "# frontmatter"


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
        if not hasattr(self.method, "__name__"):
            raise AttributeError(
                "The `include` decorator can only be applied to regular methods."
            )
        key = self.method.__name__
        if key not in self.instance._helper_registry:
            val = f"_original_{key}"
            self.instance._helper_registry[key] = val
            setattr(self.instance, val, self.method)

        return self.__call__

    def __call__(self, *args, **kwargs) -> Any:

        return self.method(self.instance, *args, **kwargs)


include = _IncludeDecorator  # alias for Include class


def get_main_source_file(src: str, argspec: NamedTuple) -> str:
    ln = []
    ln.append(src)
    ln.append("\n")
    ln.append("if __name__ == '__main__':")
    if len(argspec.args) == 0:
        ln.append(_indent("entrypoint()"))
        return "\n".join(ln)

    ln.append(_indent("import argparse"))
    ln.append(_indent("parser = argparse.ArgumentParser()"))

    for arg in argspec.args:
        if arg in ["self", "cls"]:
            continue
        assert (
            arg in argspec.annotations
        ), f"Arg {arg} is not annotated. All entrypoint args should be annotated kwargs."

    for arg, typ in argspec.annotations.items():
        if arg in ("self", "cls"):
            continue
        if hasattr(typ, "__origin__"):
            if typ.__origin__ in (list, tuple):
                nargs = "'+'"
                typ = typ.__args__[0]
            else:
                raise TypeError(
                    f"Only List and Tuple supported but get {arg} as {typ}."
                )
        else:
            nargs = None

        type_name = typ.__name__ if hasattr(typ, "__name__") else None
        ln.append(
            _indent(f"parser.add_argument('--{arg}', type={type_name}, nargs={nargs})")
        )
    ln.append(_indent("kwargs = vars(parser.parse_args())"))
    ln.append(_indent("entrypoint(**kwargs)"))

    return "\n".join(ln)


def get_function_source(
    method: Callable, name: Optional[str] = None
) -> Tuple[str, str]:
    """method or function -> inner source, outter source (to be moved to
    frontmatter of `main.py`)"""

    if name is None:
        name = method.__name__

    lines = inspect.getsource(method).split("\n")
    skip_lines = 0
    for ln in lines:
        if ln.lstrip().startswith("def"):
            break
        else:
            skip_lines += 1
    lines = lines[skip_lines:]

    # get global indent spaces
    global_indent = len(lines[0].split("def ")[0])
    assert (
        global_indent % INDENT == 0
    ), f"Method source indent ({global_indent}) is not in units of {INDENT} where the first line is {lines[0]}"
    global_indent = global_indent // INDENT

    # remove global indent spaces
    lines = (_dedent(ln, global_indent) for ln in lines[1:])
    argspec = inspect.getfullargspec(method)
    first_non_self_arg = 0
    for arg in argspec.args:
        if arg in ["self", "cls"]:
            first_non_self_arg += 1
            break
    inner = [
        f"def {name}({', '.join(argspec.args[first_non_self_arg:])}):"
    ]  # do not include `self` or `cls` if present
    outter = []
    for ln in lines:
        if ln.strip() == "":
            continue
        ln = ln.rstrip()
        if ln.endswith(_fm):
            outter.append(ln[: -len(_fm)].strip())
        else:
            inner.append(ln)

    return "\n".join(inner), "\n".join(outter)
