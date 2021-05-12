from typing import *

class JarBase:

    def __init__(self, base_image: str, **kwargs):
        self.base_image = base_image
        self.dockerfile_lines = [f'FROM {self.base_image}'] 
        self.setup_image(**kwargs)

    def setup_image(self, **kwargs):
        raise NotImplementedError('Please setup docker image here.')

    def entrypoint(self, **kwargs):
        raise NotImplementedError('Entry point ops should be implemented here.')

    def FROM(self, base_image: str):
        self.dockerfile_lines.append(f'FROM {base_image}')

    def ENV(self, *args):
        for arg in args:
            self.dockerfile_lines.append(f'ENV {arg}')

    def RUN(self, *args):
        for arg in args:
            self.dockerfile_lines.append(f'RUN {arg}')

    def COPY(self, out_dir, in_dir, flag=None):
        if flag:
            self.dockerfile_lines.append(f'COPY {flag} {out_dir} {in_dir}')
        else:
            self.dockerfile_lines.append(f'COPY {out_dir} {in_dir}')

    def CMD(self, *args):
        for arg in args:
            self.dockerfile_lines.append(f'CMD {arg}')

    def EXPOSE(self, port: str):
        self.dockerfile_lines.append(f'EXPOSE {port}')

    def USER(self, user: str):
        self.dockerfile_lines.append(f'USER {user}')

    def WORKDIR(self, path):
        self.dockerfile_lines.append(f'WORKDIR {path}')
