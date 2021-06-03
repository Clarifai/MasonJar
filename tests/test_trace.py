import mason.trace as trace


def test_indent_detent():

    line = "abc"
    assert trace._indent(line) == " " * trace.INDENT + "abc"
    assert trace._indent(line, 2) == " " * trace.INDENT * 2 + "abc"

    line = trace._indent(line, 2)

    assert trace._dedent(line) == " " * trace.INDENT + "abc"
