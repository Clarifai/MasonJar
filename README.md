# Mason Jar

* Save your experiment dependencies and main function in one place as a python class
* Mirror docker layers with python inheritance
* With `mason.Jar` instances, you can 
  * test your code in eager mode
  * build image
  * test locally in container
  * login and push image

```bash
mason
├── __init__.py
├── base.py                                                                                                       
├── client.py                                                                                                     
└── trace.py 
```

## Install

`pip install mason-jar`

## Example:

### Define your container as a python class

```python
import mason

class HelloWorld(mason.Jar):
    
    base_image = 'python:3.7'
    
    def setup_image(self):
        self.RUN('python3 -m pip install numpy')

    def entrypoint(self, arg1: int, arg2: str):  # optional args, must be typed 
        import subprocess
        process = subprocess.run(['cat', '/etc/os-release'])
        print('hello world')
        import numpy as np
        print(f'numpy version {np.__version__}')
        print(np.sqrt(np.pi))
        print(f'arg1 {arg1}')
        print(f'arg2 {arg2}')
```

### Instantiate and export

```python
hello = HelloWorld()

# test in eager mode
hello(arg1=123, arg2='abc')

# hello world
# numpy version 1.20.2
# 1.7724538509055159
# arg1 123
# arg2 abc

# save to disk
hello.save()

# build image
hello.build()

# test run
hello.run(arg1=123, arg2='abc')
# PRETTY_NAME="Debian GNU/Linux 10 (buster)"
# NAME="Debian GNU/Linux"
# VERSION_ID="10"
# VERSION="10 (buster)"
# VERSION_CODENAME=buster
# ID=debian
# HOME_URL="https://www.debian.org/"
# SUPPORT_URL="https://www.debian.org/support"
# BUG_REPORT_URL="https://bugs.debian.org/"
# hello world
# numpy version 1.20.3
# 1.7724538509055159
# arg1 123
# arg2 abc
```

## Push to registry

```python
# login to registry with your credentials
hello.login('username', 'registry')
# push
info = hello.push()
```

## Expand the experiment

```python
class HelloChild(HelloWorld):
    
    def setup_image(self):  # install additional packages
        super().setup_image()
        self.RUN('python3 -m pip install scipy')

    def entrypoint(self):  # override the main function
        
        import subprocess
        subprocess.run(['cat', '/etc/os-release'])
        print('hello world')
        import numpy as np
        import scipy as sp
        print(f'numpy version {np.__version__}')
        print(f'scipy version {sp.__version__}')
        print(np.cos(np.pi))
```

### Attach constants

```python
class HelloConstants(HelloWorld):
    def constants(self):
        self.a = 0
        self.b = "1"
        self.c = 2.0
        self.d = [0, 1, 2, 3]
```

The constants will be added to the main file as follows

```python
a = 0
b = "1"
c = 2.0
d = [0, 1, 2, 3]
```

### Attach helper functions

```python
class HelloHelpers(HelloWorld):
    @mason.include
    def a_helper_func(self, a):
        print("hello world", a)
        return a ** 2
```

The helper will be added to the main file as follows

```python
def a_helper_func(a):
		print("hello world", a)
  	return a ** 2
```

### Container entrypoint

```bash
docker run -it your.registry:helloworld python3 /entrypoint/main.py --arg1 1 --arg2 2 ...
```
