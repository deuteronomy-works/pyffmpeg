# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='pyffmpeg',
    version='0.0.1',
    description='FFmpeg wrapper for python',
    long_description="""FFmpeg wrapper for python
    """,
    url='https://github.com/deuteronomy-works/pyffmpeg',
    author='Amoh - Gyebi Godwin Ampofo Michael',
    author_email='amohgyebigodwin@gmail.com',
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords='ffmpeg, audio',
    packages=find_packages(),
)
