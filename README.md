# Pickle Your Container

Save your experiment dependencies and main function in one place as a python class.

```bash
mason
├── __init__.py
├── base.py
└── client.py
```

## Example:

### Step 1: Define your container as a python class

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

### Step 2: Instantiate and export

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

## Step 3: Push to registry

```python
# login to registry with your credentials
hello.login('username', 'registry')
# push
info = hello.push()
```

## Step 4: Expand the experiment

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

