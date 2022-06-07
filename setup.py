import pathlib
import os

from setuptools import find_packages, setup
from typing import List

HERE = os.path.abspath(os.path.dirname(__file__))
HERE_PATH = pathlib.Path(HERE)


def read(rel_path: str) -> str:
    with open(os.path.join(HERE, rel_path)) as fp:
        return fp.read()


def read_requirements(path: str) -> List[str]:
    contents = read(path)
    return contents.splitlines()


setup(
    name='podap',
    version='0.0.1',
    description='Pomodoro Day Planner',
    url='',
    author='Dennis Sitelew',
    author_email='yowidin@gmail.com',
    license='MIT',
    packages=find_packages(exclude=('test',)),
    scripts=[
        'bin/podap',
    ],
    install_requires=read_requirements("requirements.txt"),
    zip_safe=False,
)
