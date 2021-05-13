import jar


class HelloWorld(jar.JarBase):
    def setup_image(self):
        pass

    def entrypoint(self):
        print("hello world!")


def test_base():

    helloworld = HelloWorld("python:3.7")
    helloworld.save()
