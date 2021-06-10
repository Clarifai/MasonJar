import mason


def test_docker_client():
    try:
        mason.client.get_docker_client()
    except ImportError as e:
        print(e)
