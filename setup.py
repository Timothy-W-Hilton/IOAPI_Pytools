try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': ('A collection of wrapper functions'
                    ' for the Models-3 I/O API'),
    'author': 'Timothy W. Hilton',
    'url': 'thilton@ucmerced.edu',
    'download_url': 'thilton@ucmerced.edu',
    'author_email': 'thilton@ucmerced.edu',
    'version': '1.0',
    'install_requires': ['numpy'],
    'packages': ['IOAPIPytools'],
    'scripts': [],
    'name': 'IOAPIPytools'
}

setup(package_dir={'IOAPIPytools': 'IOAPIpytools'},
      package_data={'IOAPIPytools': ['IOAPIpytools/data/*']},
      include_package_data=True,
      **config)
