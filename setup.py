from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("pixel_converter.pyx")
)
