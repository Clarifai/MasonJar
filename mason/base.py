import os
import inspect
from typing import *
from .client import get_docker_client, login, push
from . import trace

__all__ = ["Jar"]


class Jar:
    """Jar Base Class."""

    REPR_INDENT = 2
    base_image: str
    registry: str = ""
    _helper_registry: Dict[
        str, str
    ]  # eager reference name `method_name` -> graph `_original_method_name`

    def __init__(self, root: str = ".", py3: bool = True, **kwargs: Any):
        self.python = "python3" if py3 else "python"
        self.dockerfile_lines = [f"FROM {self.base_image}"]
        self.setup_image(**kwargs)
        self.container_name = self.__class__.__name__.lower()
        self.path = os.path.join(root, f"{self.container_name}")
        self.COPY("main.py", f"/entrypoint/")
        self._helper_registry = {}
        self._helper_registry["entrypoint"] = "entrypoint"

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

    @property
    def main_file_source(self):
        sources = []
        for eager_name, graph_name in self._helper_registry.items():
            sources.append(
                trace.get_function_source(getattr(self, graph_name), eager_name)
            )

        source = "\n".join(sources)
        argspec = inspect.getfullargspec(self.entrypoint)
        return trace.get_main_source_file(source, argspec)

    def save(self):
        os.makedirs(self.path, exist_ok=False)
        with open(os.path.join(self.path, "Dockerfile"), "w") as f:
            f.write(self.dockerfile)

        with open(os.path.join(self.path, "main.py"), "w") as f:
            f.write(self.main_file_source)

    def build(self):
        cli = get_docker_client()

        image, logs = cli.images.build(
            path=self.path, tag=self.container_name, quiet=False
        )

        return image, logs

    def run(self, *args, **kwargs):
        if len(args) > 0:
            raise ValueError("Only kwargs are allowed.")

        cli = get_docker_client()
        arg_string = " ".join((f"--{name} {value}" for name, value in kwargs.items()))
        cmd = f"{self.python} /entrypoint/main.py " + arg_string

        print(cli.containers.run(self.container_name, command=cmd).decode())

    def login(
        self, username: str, registry: str, password: Optional[str] = None, **kwargs
    ):

        info = login(username, registry, password, **kwargs)
        self.registry = registry

        return info

    def push(self, verbose: bool = True):

        if self.registry is None:
            raise ValueError("Registry should not be empty. Please login first.")

        cli = get_docker_client()
        image = cli.images.get(self.container_name)
        registry_tag = f"{self.registry}:{self.container_name}"
        image.tag(registry_tag, tag=self.container_name)

        info = push(registry_tag, verbose)

        return info

    @staticmethod
    def docker_client():
        return get_docker_client()

    def __repr__(self):
        lines = []
        lines.append(self.__class__.__name__)
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            if isinstance(v, (list, tuple, set)):
                lns = []
                lns.append(" " * self.REPR_INDENT + f"{k}:")
                for x in v:
                    ln = " " * 2 * self.REPR_INDENT + f"{x}"
                    lns.append(ln)
                lines.append("\n".join(lns))
            elif isinstance(v, dict):
                lns = []
                lns.append(" " * self.REPR_INDENT + f"{k}:")
                for _k, _v in v.items():
                    ln = " " * 2 * self.REPR_INDENT + f"{_k}: {_v}"
                    lns.append(ln)
                lines.append("\n".join(lns))
            else:
                ln = " " * self.REPR_INDENT + f"{k}: {v}"
                lines.append(ln)

        return "\n".join(lines)
