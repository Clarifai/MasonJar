import mason


class HelloWorld(mason.Jar):

    base_image = "python:3.7"

    def setup_image(self):
        self.RUN("python3 -m pip install numpy")
        self.COPY(out_dir="out_dir", in_dir="in_dir")
        self.WORKDIR("/home/mason/")
        self.add_path_mirror("in_dir", eager_path="out_dir", graph_path="in_dir")
        self.add_path_mirror("workdir", eager_path=self.path, graph_path="/home/mason/")

    def entrypoint(self):
        print("hello world")
        print(self.path_dict["workdir"])
        print(self.path_dict["in_dir"])


def test_path_registry():

    hello = HelloWorld()

    assert "in_dir" in hello._path_registry

    assert "workdir" in hello._path_registry
    assert hello.path == hello._eager_path_dict()["workdir"]
    assert "/home/mason/" == hello._graph_path_dict()["workdir"]

    hello = HelloWorld("newroot")

    assert "workdir" in hello._path_registry
    assert hello.path == hello._eager_path_dict()["workdir"]
    assert "/home/mason/" == hello._graph_path_dict()["workdir"]


def test_mainfile():

    hello = HelloWorld()

    assert "path_dict" in hello.mainfile

    hello()
