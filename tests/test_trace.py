import mason.trace as trace


def test_indent_detent():

    line = "abc"
    assert trace._indent(line) == " " * trace.INDENT + "abc"
    assert trace._indent(line, 2) == " " * trace.INDENT * 2 + "abc"

    line = trace._indent(line, 2)

    assert trace._dedent(line) == " " * trace.INDENT + "abc"


# do not change the format of the following functions!
def example_method(a):
    return a ** 2


def example_static_method(a):
    return a ** 2


def example_class_method(a):
    return a ** 2


# do not change the format of the above functions!


def test_inner_source():

    import inspect

    class Example:
        def example_method(self, a: int):
            return a ** 2

        @staticmethod
        def example_static_method(a: int):
            return a ** 2

        @classmethod
        def example_class_method(cls, a: int):
            return a ** 2

    ex = Example()

    ex_method = trace.get_function_source(ex.example_method)[0]
    ex_static_method = trace.get_function_source(ex.example_static_method)[0]
    ex_class_method = trace.get_function_source(ex.example_class_method)[0]

    assert ex_method.rstrip("\n") == inspect.getsource(example_method).rstrip("\n")
    assert ex_static_method.rstrip("\n") == inspect.getsource(
        example_static_method
    ).rstrip("\n")
    assert ex_class_method.rstrip("\n") == inspect.getsource(
        example_class_method
    ).rstrip("\n")


def test_outter_source():
    class Example:
        def example_method(self, a: int):
            import math  # frontmatter

            return a ** 2

        @staticmethod
        def example_static_method(a: int):
            import math  # frontmatter

            return a ** 2

        @classmethod
        def example_class_method(cls, a: int):
            import math  # frontmatter

            return a ** 2

    ex = Example()

    ex_method = trace.get_function_source(ex.example_method)[1]
    ex_static_method = trace.get_function_source(ex.example_static_method)[1]
    ex_class_method = trace.get_function_source(ex.example_class_method)[1]

    assert ex_method == "import math"
    assert ex_static_method == "import math"
    assert ex_class_method == "import math"
