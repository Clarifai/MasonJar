import inspect
import os
from typing import *

from . import trace
from .client import get_docker_client, login, push
from .path import PathMirror

__all__ = ["Jar"]

_DEFAULT_REGISTRY = "registry.hub.docker.com"


class Jar:
    """
    Jar Base Class.

    Usage:

    Step 1: Declare `base_image`

    ```
        class MyImage(Jar):
            base_image = 'ubuntu:latest'
            ...
    ```
    Step 2: Define `setup_image`

    ```
    class MyImage(Jar):

        base_image = 'ubuntu:latest'

        def setup_image(self):
            pass
    ```

    Step 3: Define `entrypoint`
    ```
    class MyImage(Jar):

        base_image = 'ubuntu:latest'

        def setup_image(self):
            pass

        def entrypoint(self, x: int):
            print(x ** 2)
    ```

    Use `constants` to attach optional constants which will be exported in main
    file

    Use `@include` to attach optional helper methods which will be exported in
    main file as functions

    Use `save` to save Dockerfile and main file to a folder in root directory

    Use `build` to build image

    Use `run` to run the mainfile in docker image

    Use `login` to login your registry

    Use `push` to push your image to registry

    Params:

    __init__(root, py3, **kwargs)
        `root`, str: root directory, default '.'
        `py3`, bool: is python3, default True
    """

    REPR_INDENT = 2
    base_image: str
    registry: Optional[str] = None
    # eager reference name `method_name` -> graph `_original_method_name`
    _helper_registry: Dict[str, str]
    # constants to be included in the main file
    _constant_registry: Dict[str, Any]
    # path registry: human readable name -> PathMirror(eager_path, graph_path)
    _path_registry: Dict[str, PathMirror]

    def __init__(self, root: str = ".", py3: bool = True, **kwargs: Any):
        self.python = "python3" if py3 else "python"
        self.container_name = self.__class__.__name__.lower()
        self.path = os.path.join(root, f"{self.container_name}")
        self._path_registry = {}
        self.dockerfile_lines = [f"FROM {self.base_image}"]
        self.setup_image(**kwargs)
        self.COPY("main.py", "/entrypoint/")
        self._constant_registry = {}

        self.constants()
        self._helper_registry = {}
        self._helper_registry["entrypoint"] = "entrypoint"
        self._record_methods()

    def _record_methods(self):
        _exclude = {
            "_helper_registry",
            "_constant_registry",
            "dockerfile",
            "mainfile",
            "entrypoint",
            "setup_image",
        }
        for attr in dir(self.__class__):
            if attr in _exclude or attr.startswith("__"):
                continue
            _ = getattr(self, attr)

    def setup_image(self, **kwargs):
        raise NotImplementedError("Please setup docker image here.")

    def entrypoint(self, **kwargs):
        raise NotImplementedError("Entry point ops should be implemented here.")

    def constants(self):
        """Define constants here."""

    def add_path_mirror(self, path_name: str, eager_path: str, graph_path: str):
        self._path_registry[path_name] = PathMirror(eager_path, graph_path)

    def get_eager_path(self, path_name: str):
        if path_name in self._path_registry:
            return self._path_registry[path_name].eager_path
        else:
            raise ValueError(f"Path name {path_name} does not exist")

    def get_graph_path(self, path_name: str):
        if path_name in self._path_registry:
            return self._path_registry[path_name].graph_path
        else:
            raise ValueError(f"Path name {path_name} does not exist")

    @property
    def path_dict(self):
        return self._eager_path_dict()

    def _eager_path_dict(self):
        return {name: mirror.eager_path for name, mirror in self._path_registry.items()}

    def _graph_path_dict(self):
        return {name: mirror.graph_path for name, mirror in self._path_registry.items()}

    def __setattr__(self, key: str, value: Any):
        """Record constants after instance created."""
        if hasattr(self, "_constant_registry") and not key.startswith("_"):
            self._constant_registry[key] = value

        object.__setattr__(self, key, value)

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

    def ADD(self, out_dir: str, in_dir: str):
        self.dockerfile_lines.append(f"ADD {out_dir} {in_dir}")

    def COPY(self, out_dir: str, in_dir: str, flag: Optional[str] = None):
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
    def mainfile(self):
        sources = []
        constants = []
        frontmatters = []
        for name, value in self._constant_registry.items():
            if isinstance(value, str):
                value = f"'{value}'"
            constants.append(f"{name} = {value}")

        if self.path_dict:
            constants.append(f"path_dict = {self._graph_path_dict()}")

        for eager_name, graph_name in self._helper_registry.items():
            source, frontmatter = trace.get_function_source(
                getattr(self, graph_name), eager_name
            )
            if len(source) > 0:
                sources.append(source)
            if len(frontmatter) > 0:
                frontmatters.append(frontmatter)

        mainsource = [
            "\n".join(frontmatters),
            "\n" if len(frontmatters) > 0 else "",
            "\n".join(constants),
            "\n" if len(constants) > 0 else "",
            "\n".join(sources),
        ]
        argspec = inspect.getfullargspec(self.entrypoint)
        return trace.get_main_source_file("\n".join(mainsource), argspec).replace(
            "self.", ""
        )

    def save(self, overwrite=True):
        os.makedirs(self.path, exist_ok=overwrite)
        with open(os.path.join(self.path, "Dockerfile"), "w") as f:
            f.write(self.dockerfile)

        with open(os.path.join(self.path, "main.py"), "w") as f:
            f.write(self.mainfile)

    def build(self):
        cli = get_docker_client()

        image, logs = cli.images.build(
            path=self.path, tag=self.container_name, quiet=False
        )

        return image, logs

    def run(self, *args, **kwargs):
        if len(args) > 0:
            raise ValueError("Only kwargs are allowed.")

        def _parse_list(x):
            if isinstance(x, (list, tuple)):
                return " ".join(str(i) for i in x)
            else:
                return x

        cli = get_docker_client()
        arg_string = " ".join(
            (f"--{name} {_parse_list(value)}" for name, value in kwargs.items())
        )
        print(f">> input args >> {arg_string}\n")
        cmd = f"{self.python} /entrypoint/main.py " + arg_string

        print(cli.containers.run(self.container_name, command=cmd).decode())

    def login(
        self,
        username: str,
        registry: str = _DEFAULT_REGISTRY,
        password: Optional[str] = None,
        **kwargs,
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
