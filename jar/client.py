import getpass
from typing import Optional


def get_docker_client():

    try:
        import docker
    except ImportError:
        raise ImportError("Please install docker python client: `pip install docker`")

    return docker.client.from_env()


def login(username: str, registry: str, password: Optional[str] = None, **kwargs):

    if not password:
        password = getpass.getpass()

    cli = get_docker_client()
    output = cli.login(
        username=username, password=password, registry=registry, **kwargs
    )

    return output


def push(tag, verbose: bool = True):
    cli = get_docker_client()
    logs = []
    for l in cli.images.push(tag, stream=True, decode=True):
        if verbose:
            print(l)
        logs.append(l)

    return logs
