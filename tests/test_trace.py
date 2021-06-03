import mason.trace as trace


def test_indent_detent():

    line = "abc"
    assert trace._indent(line) == " " * trace.INDENT + "abc"
    assert trace._indent(line, 2) == " " * trace.INDENT * 2 + "abc"

    line = trace._indent(line, 2)

    assert trace._dedent(line) == " " * trace.INDENT + "abc"


class Example:
    def example_method(self, a: int):
        return a ** 2

    @staticmethod
    def examples_static_method(a: int):
        return a ** 2


def test_method_to_function_source():

    ex = Example()

    ex_method = trace.method_to_function_source(ex.example_method)
    ex_static_method = trace.method_to_function_source(ex.examples_static_method, 1)

    exec(ex_method)
    exec(ex_static_method)

    assert ex.example_method(10) == example_method(10)
    assert Example.examples_static_method(100) == examples_static_method(100)
