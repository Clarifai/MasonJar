import mason


class HelloWorld(mason.Jar):

    base_image = "python:3.7"

    def setup_image(self):
        self.RUN("python3 -m pip install numpy")

    def entrypoint(self):
        print("hello world")
        import numpy as np

        print(f"numpy version {np.__version__}")


def test_base():

    HelloWorld()
