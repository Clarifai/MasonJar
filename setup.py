from setuptools import find_packages, setup

# load readme
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="mason-jar",
    version="0.1.0",
    description="Pickle your container as a python class.",
    packages=find_packages(exclude=["tests"]),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["docker"],
    license="MIT",
)
