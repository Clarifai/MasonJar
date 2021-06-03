import mason.trace as trace


def test_indent_detent():

    line = "abc"
    assert trace._indent(line) == " " * trace.INDENT + "abc"
    assert trace._indent(line, 2) == " " * trace.INDENT * 2 + "abc"

    line = trace._indent(line, 2)

    assert trace._dedent(line) == " " * trace.INDENT + "abc"


def test_method_to_function_source():
    class Example:
        def example_method(self, a: int):
            return a ** 2

        @staticmethod
        def example_static_method(a: int):
            return a ** 2

        @classmethod
        def example_class_method(cls, a: int):
            return a ** 2

    def example_method(a: int):
        return a ** 2

    def example_static_method(a: int):
        return a ** 2

    def example_class_method(a: int):
        return a ** 2

    ex = Example()

    ex_method = trace.method_to_function_source(ex.example_method)
    ex_static_method = trace.method_to_function_source(ex.example_static_method, 1)
    trace.method_to_function_source(ex.example_class_method, 1)

    assert ex.example_method(10) == example_method(10), ex_method
    assert Example.example_static_method(100) == example_static_method(
        100
    ), ex_static_method
