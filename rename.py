import sys
import os
from glob import glob

version = sys.argv[1]

# "cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"

lists = glob('./dist/*.whl')
oss = {
    'win32': 'py3-none-win32.whl',
    'amd64': 'py3-none-win_amd64.whl',
    'linux_intel': "py3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
    'linux_aarch': "py3-manylinux_2_17_aarch64.manylinux2014_aarch64.whl",
    'macos11': "py3-macosx_11_0_arm64.whl",
    'macos_intel': "py3-macosx_10_9_x86_64.whl",
    'macos_uni': "py3-macosx_10_9_universal2.whl"}

for x in lists:
    if '-any' in x:
        na = x.split('-', 2)[:2]

        na.append(oss[version])
        print(na)
        new_name = '-'.join(na)
        os.rename(x, new_name)
