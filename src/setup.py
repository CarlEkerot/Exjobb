from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(name="align",
      version='0.1',
      description='Global and local sequence alignment implemented in C with a Cython wrapper.',
      author='Fredrik Appelros, Carl Ekerot',
      author_email='fredrik.appelros@gmail.com, kalle@implode.se',
      url='https://github.com/FredrikAppelros/align',
      py_modules=['align'],
      install_requires=['numpy', 'cython'],
      cmdclass = {'build_ext': build_ext},
      ext_modules = [Extension('align', ['align.pyx', 'calign.c'])],
)
