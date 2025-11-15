from setuptools import setup

setup(
    name="my_test_pkg",
    version="1.0.0",
    install_requires=[
        "requests>=2.25.0",
        "click",
        "colorama; sys_platform == 'win32'",
    ],
)