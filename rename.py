import sys
import os
from glob import glob

version = sys.argv[1]

lists = glob('./dist/*.whl')
oss = {
    'win32': 'py3-none-win32.whl',
    'amd64': 'py3-none-win_amd64.whl',
    'macos15': 'py3-abi3-macosx_10_14_x86_64.whl',
    'macos': 'py3-abi3-macosx_10_6_intel.whl',
    'linux': 'py3-abi3-manylinux2010_x86_64.whl',
    'centos': 'py3-abi3-manylinux2014_x86_64.whl'}

for x in lists:
    if '-any' in x:
        na = x.split('-', 2)[:2]
        na.append(oss[version])
        print(na)
        new_name = '-'.join(na)
        os.rename(x, new_name)
