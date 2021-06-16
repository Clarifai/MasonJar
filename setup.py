from setuptools import find_packages, setup

from mason import __version__

# load readme
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="mason-jar",
    version=__version__,
    description="Pickle your containerized experiment as a python class.",
    packages=find_packages(exclude=["tests"]),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["docker"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
    ],
    keywords="docker container experiment",
    license="MIT",
)
