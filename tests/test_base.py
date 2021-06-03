import mason


class HelloWorld(mason.Jar):

    base_image = "python:3.7"

    def setup_image(self):
        self.RUN("python3 -m pip install numpy")

    def entrypoint(self):
        print("hello world")


def test_base():

    hello = HelloWorld()
    print(hello.dockerfile)
    print(hello.main_file_source)
