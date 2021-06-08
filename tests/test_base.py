import mason
import tempfile


class HelloWorld(mason.Jar):

    base_image = "python:3.7"

    def setup_image(self):
        self.RUN("python3 -m pip install numpy")

    def entrypoint(self):
        print("hello world")


class HelloConstants(HelloWorld):
    def constants(self):
        self.a = 0
        self.b = "1"
        self.c = 2.0
        self.d = [0, 1, 2, 3]


class HelloHelpers(HelloWorld):
    @mason.include
    def a_helper_func(self, a):
        print("hello world", a)


def test_jar_files():

    hello = HelloWorld()
    hello()

    dockerfile = hello.dockerfile
    assert "FROM python:3.7" in dockerfile
    assert "RUN python3 -m pip install numpy" in dockerfile
    mainfile = hello.mainfile
    assert 'print("hello world")' in mainfile


def test_save():

    with tempfile.TemporaryDirectory() as td:
        hello = HelloWorld(root=td)
        hello.save()


def test_registry():

    assert mason.Jar.registry is None

    hello = HelloWorld()
    hello.registry = "my.registry"

    assert hello.registry == "my.registry"
    assert mason.Jar.registry is None

    HelloWorld.registry = "another.registry"
    assert hello.registry == "my.registry"


def test_constants():

    hello = HelloConstants()
    assert hello.a == hello._constant_registry["a"] == 0
    assert hello.b == hello._constant_registry["b"] == "1"
    assert hello.c == hello._constant_registry["c"] == 2.0
    assert hello.d == hello._constant_registry["d"] == [0, 1, 2, 3]
    hello.e = dict(a=1, b=2)
    assert hello.e == hello._constant_registry["e"] == dict(a=1, b=2)


def test_helpers():

    hello = HelloHelpers()

    assert "a_helper_func" in hello._helper_registry
