import os
from setuptools import find_packages, setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name             = 'FAUSTPy',
    version          = '0.1',
    url              = 'https://github.com/marcecj/faust_python',
    download_url     = 'https://github.com/marcecj/faust_python',
    license          = 'MIT',
    author           = 'Marc Joliet',
    author_email     = 'marcec@gmx.de',
    description      = 'FAUSTPy is a Python wrapper for the FAUST DSP language.',
    packages         = ['FAUSTPy'],
    test_suite       = "test.tests",
    long_description = read('README.md'),
    platforms        = 'any',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Topic :: Multimedia :: Sound/Audio'
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
