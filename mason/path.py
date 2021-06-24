from dataclasses import dataclass


@dataclass
class PathMirror:

    eager_path: str  # path used in python dev env
    graph_path: str  # actual path in the container
