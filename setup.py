try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'A collection of wrapper functions for the Models-3 I/O API',
    'author': 'Timothy W. Hilton',
    'url': 'thilton@ucmerced.edu',
    'download_url': 'thilton@ucmerced.edu',
    'author_email': 'thilton@ucmerced.edu',
    'version': '0.1',
    'install_requires': ['numpy'],
    'packages': ['ioapi_pytools'],
    'scripts': [],
    'name': 'IOAPIpytools'
}

setup(**config)
