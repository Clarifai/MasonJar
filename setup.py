from setuptools import find_packages, setup
from mason import __version__

# load readme
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="mason-jar",
    version=__version__,
    description="Pickle your container as a python class.",
    packages=find_packages(exclude=["tests"]),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["docker"],
    license="MIT",
)
