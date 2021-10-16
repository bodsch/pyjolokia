
import sys
from setuptools import setup, Command

kw = {}

#if sys.version_info >= (3,):
#    kw['use_2to3'] = True

class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        #import sys
        import subprocess
        errno = subprocess.call(
          [
              sys.executable,
              'runtests.py',
              'tests.py'
          ]
        )
        raise SystemExit(errno)


setup(
    name='pyjolokia',
    version='0.4.0',
    description='Pure Python based Jolokia client',
    author='Colin Wood',
    license="Apache License Version 2.0",
    author_email='bodo@boone-schulz.de',
    py_modules=['pyjolokia'],
    url='https://github.com/bodsch/pyjolokia',
    download_url='http://github.com/bodsch/sshed/tarball/master',
    long_description=open('README.rst').read(),
    include_package_data=True,
    keywords=['jolokia', 'jmx'],
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 4 - Beta'
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Java Libraries',
    ],
    **kw
)
