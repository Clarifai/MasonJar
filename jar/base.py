import os
import inspect

__all__ = ["JarBase"]

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
        ln.append(" " * INDENT + f"parser.add_argument('--{arg}', type={typ.__name__})")
    ln.append(" " * INDENT + "kwargs = vars(parser.parse_args())")
    ln.append(" " * INDENT + "main(**kwargs)")
    return "\n".join(ln)


def get_docker_client():

    try:
        import docker
    except ImportError:
        raise ImportError("Please install docker python client: `pip install docker`")

    return docker.client.from_env()


class JarBase:
    """Jar Base Class."""

    base_image: str

    def __init__(self, root: str = ".", py3: bool = True, **kwargs):
        self.python = "python3" if py3 else "python"
        self.dockerfile_lines = [f"FROM {self.base_image}"]
        self.setup_image(**kwargs)
        self.container_name = self.__class__.__name__
        self.path = os.path.join(root, f"{self.container_name}")
        self.COPY("main.py", f"/{self.container_name}/")

    def setup_image(self, **kwargs):
        raise NotImplementedError("Please setup docker image here.")

    def entrypoint(self, **kwargs):
        raise NotImplementedError("Entry point ops should be implemented here.")

    def __call__(self, *args, **kwargs):
        if len(args) > 0:
            raise ValueError("Only kwargs are allowed.")
        self.entrypoint(**kwargs)

    def ENV(self, *args):
        for arg in args:
            self.dockerfile_lines.append(f"ENV {arg}")

    def RUN(self, *args):
        for arg in args:
            self.dockerfile_lines.append(f"RUN {arg}")

    def COPY(self, out_dir, in_dir, flag=None):
        if flag:
            self.dockerfile_lines.append(f"COPY {flag} {out_dir} {in_dir}")
        else:
            self.dockerfile_lines.append(f"COPY {out_dir} {in_dir}")

    def CMD(self, *args):
        for arg in args:
            self.dockerfile_lines.append(f"CMD {arg}")

    def EXPOSE(self, port: str):
        self.dockerfile_lines.append(f"EXPOSE {port}")

    def USER(self, user: str):
        self.dockerfile_lines.append(f"USER {user}")

    def WORKDIR(self, path):
        self.dockerfile_lines.append(f"WORKDIR {path}")

    @property
    def dockerfile(self):
        return "\n".join(self.dockerfile_lines)

    def save(self):
        os.makedirs(self.path, exist_ok=False)
        with open(os.path.join(self.path, "Dockerfile"), "w") as f:
            f.write(self.dockerfile)
        lines = inspect.getsource(self.entrypoint).split("\n")
        argspec = inspect.getfullargspec(self.entrypoint)
        for arg in argspec.args:
            if arg == "self":
                continue
            assert (
                arg in argspec.annotations
            ), f"Arg {arg} is not annotated. All args should we annotated kwargs."
        source = [f"def main({', '.join(argspec.args[1:])}):"]  # do not include `self`
        for ln in lines[1:]:
            source.append(ln[INDENT:])
        source = "\n".join(source)
        with open(os.path.join(self.path, "main.py"), "w") as f:
            f.write(get_main(source, argspec))

    def build(self):
        cli = get_docker_client()

        image, logs = cli.images.build(
            path=self.path, tag=self.container_name.lower(), quiet=False
        )

        get_docker_client()

        return image, logs

    def run(self, *args, **kwargs):
        if len(args) > 0:
            raise ValueError("Only kwargs are allowed.")

        cli = get_docker_client()
        arg_string = " ".join((f"--{name} {value}" for name, value in kwargs.items()))
        cmd = f"{self.python} /{self.container_name}/main.py " + arg_string

        print(cli.containers.run(self.container_name.lower(), command=cmd).decode())

    @staticmethod
    def docker_client():
        return get_docker_client()
