# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import re
import os


version = os.environ['GITHUB_REF'].split('/')[-1]
print(f'version: {version}')


with open('README.md', 'r') as rm:
    long_desc = rm.read()


sta = 'Development Status :: 5 - Production/Stable'
bta = 'Development Status :: 4 - Beta'
dev_status = sta

ver = version.split('-')[0]
ver = ver.replace('v', '')

if 'beta' in version:
    beta = version.split('-')[1]
    beta = beta.split('beta.')[1]
    ver += f'b{beta}'
    dev_status = bta


setup(
    name='pyffmpeg',
    version=f'{ver}',
    description='FFmpeg wrapper for python',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    url='https://github.com/deuteronomy-works/pyffmpeg',
    author='Amoh - Gyebi Godwin Ampofo Michael',
    author_email='amohgyebigodwin@gmail.com',
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        f"{dev_status}",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords='''ffmpeg, FFmpeg, ffprobe, FFprobe,
    album art, cover art, metadata,
    conversion, converting, audio, video''',
    packages=find_packages(),
)
