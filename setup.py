from setuptools import find_packages, setup

# load readme
with open("README.md", "r") as f:
    long_description = f.read()


def version():
    import mason

    return mason.__version__


setup(
    name="mason-jar",
    version=version(),
    description="Pickle your container as a python class.",
    packages=find_packages(exclude=["tests"]),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["docker"],
    license="MIT",
)
