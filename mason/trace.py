from typing import *

INDENT = 4


def _indent(line: str, num_tabs: int = 1) -> str:
    return " " * INDENT * num_tabs + line


def _dedent(line: str) -> str:
    return line[num_tabs * INDENT :]


def get_main(src: str, argspec: NamedTuple):
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
            " " * INDENT
            + f"parser.add_argument('--{arg}', type={typ.__name__}, nargs={nargs})"
        )
    ln.append(" " * INDENT + "kwargs = vars(parser.parse_args())")
    ln.append(" " * INDENT + "main(**kwargs)")
    return "\n".join(ln)


def method_to_function(method: Callable):
    pass
