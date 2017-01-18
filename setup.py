try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': ('A collection of wrapper functions'
                    ' for the EDSS Models-3 I/O API'),
    'author': 'Timothy W. Hilton',
    'url': 'https://github.com/Timothy-W-Hilton/IOAPI_Pytools',
    'download_url': 'https://github.com/Timothy-W-Hilton/IOAPI_Pytools',
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
