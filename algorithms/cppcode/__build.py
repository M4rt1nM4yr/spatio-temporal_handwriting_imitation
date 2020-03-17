from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import setuptools

import os as os
import glob as glob


class get_pybind_include(object):
    """Helper class to determine the pybind11 include path
    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14] compiler flag.
    The c++14 is prefered over c++11 (when it is available).
    """
    if has_flag(compiler, '-std=c++14'):
        return '-std=c++14'
    elif has_flag(compiler, '-std=c++11'):
        return '-std=c++11'
    else:
        raise RuntimeError('Unsupported compiler -- at least C++11 support '
                           'is needed!')


class BuildExt(build_ext):

    import sys

    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc'],
        'unix': [],
    }

    if sys.platform == 'darwin':
        c_opts['unix'] += ['-stdlib=libc++', '-mmacosx-version-min=10.7']

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        if ct == 'unix':
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)


def build():
    cwd_bup = os.getcwd()

    try:
        modulePath = os.path.dirname(os.path.realpath(__file__))
        print("Building library '" + os.path.basename(modulePath) + "' ...")

        os.chdir(modulePath)

        sources = glob.glob('__src/**/*.cpp', recursive=True)
        # print("   Sources:", sources)

        module1 = Extension('__lib',
                            sources=sources,
                            include_dirs=[
                                # Path to pybind11 headers
                                get_pybind_include(),
                                get_pybind_include(user=True)
                            ],
                            language='c++'
                            )

        setup(name='__lib',
              ext_modules=[module1],
              script_args=["build_ext", "--inplace", "-q"],
              cmdclass={'build_ext': BuildExt},
              )

    finally:
        os.chdir(cwd_bup)
