INDENT = 4


def get_main(src, argspec):
    ln = []
    ln.append(src)
    ln.append("if __name__ == '__main__':")
    ln.append(" " * INDENT + "import argparse")
    ln.append(" " * INDENT + "parser = argparse.ArgumentParser()")
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
