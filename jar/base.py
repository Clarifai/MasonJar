import os
import inspect
import abc

__all__ = ["JarBase"]

INDENT = 4


def get_main(src):
    ln = []
    ln.append(src)
    ln.append("if __name__ == '__main__':")
    ln.append(" " * INDENT + "main()")
    return "\n".join(ln)


class JarBase:
    """Jar Base Class"""

    base_image: str

    def __init__(self, root: str = ".", py3: bool = True, **kwargs):
        self.python = "python3" if py3 else "python"
        self.dockerfile_lines = [f"FROM {self.base_image}"]
        self.setup_image(**kwargs)
        self.container_name = self.__class__.__name__
        self.path = os.path.join(root, f"{self.container_name}")
        self.COPY("main.py", f"/{self.container_name}/")
        self.CMD(f"{self.python} /{self.container_name}/main.py")

    def setup_image(self, **kwargs):
        raise NotImplementedError("Please setup docker image here.")

    def entrypoint(self):
        raise NotImplementedError("Entry point ops should be implemented here.")

    def __call__(self):
        self.entrypoint()

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
        source = ["def main():"]
        for ln in lines[1:]:
            source.append(ln[INDENT:])
        source = "\n".join(source)
        with open(os.path.join(self.path, "main.py"), "w") as f:
            f.write(get_main(source))

    def build(self):
        try:
            import docker
        except ImportError as e:
            print("Please install docker python client.")
            raise e

        cli = docker.client.from_env()
        image, logs = cli.images.build(
            path=self.path, tag=self.container_name.lower(), quiet=False
        )

        return image, logs

    def run(self):
        try:
            import docker
        except ImportError as e:
            print("Please install docker python client.")
            raise e

        cli = docker.client.from_env()
        print(cli.containers.run(self.container_name.lower()).decode())
