import sys
import os
import tarfile
import shutil
import glob
import subprocess
import requests
from py7zr import unpack_7zarchive

from pyffmpeg import misc


version = os.environ['GITHUB_REF'].split('/')[-1]
print(f'version: {version}')

_, os_name, token = sys.argv

osn = os_name.split('-')[0]
cwd = os.path.realpath('.')

bin_path = os.path.join(cwd, 'pyffmpeg/static/bin')

# Download Qmlview archive for os
# extract to folder
# copy all those contents to folder_name, skipping the existing ones



# Login to GH
with open('token.txt', 'w') as tok:
    tok.write(token)
    print('Finished writing token file')

cmd = 'gh auth login --with-token < token.txt'
os.system(cmd)
print('Authenticated')


def extract_to_folder(ffmpeg: str, arch: str, z=True) -> str:
    if z:
        shutil.register_unpack_format('7zip', ['.7z'], unpack_7zarchive)
    shutil.unpack_archive(arch, extract_dir=cwd)
    print('done with unpack')
    fpath = f'**/{ffmpeg}'
    fname = glob.glob(fpath)[0]
    return os.path.join(cwd, fname)


# Build wheel
if os_name == 'win32':
    # Download Qmlview archive for os
    os_cmd = 'gh release download --repo'
    os_cmd += ' github.com/GyanD/codexffmpeg --pattern "*full_build.7z"'
    try:
        os.system(os_cmd)
        print('done with download of winbin')
        # extract to folder
        arch = glob.glob('ffmpeg*.7z')[0]
        fullpath = extract_to_folder('ffmpeg.exe', arch)
        out = '../win32'

        misc.Paths().convert_to_py(fullpath, out)
        # copy all those contents to folder_name, skip exitsting
        win32 = os.path.join(bin_path, 'win32')
        # replace
        shutil.copy('win32.py', win32)

    except:
        print('failed trying something else')
        print(os.listdir(cwd))


if os_name == 'darwin':
    link = 'https://evermeet.cx/ffmpeg/get/ffmpeg/7z'
    resp = requests.get(link, stream=True)
    with open('ffmpeg.7z', 'wb') as z:
        for chunk in resp.iter_content(chunk_size=2048):
            if chunk:
                z.write(chunk)

    arch = glob.glob('ffmpeg*.7z')[0]
    fullpath = extract_to_folder('ffmpeg',arch)
    out = '../darwin'

    misc.Paths().convert_to_py(fullpath, out)

    darwin = os.path.join(bin_path, 'darwin')
    shutil.copy('darwin.py', darwin)

else:
    # Download Qmlview archive for os
    link = 'https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-i686-static.tar.xz'
    resp = requests.get(link, stream=True)
    with open('ffmpeg.tar.xz', 'wb') as z:
        for chunk in resp.iter_content(chunk_size=2048):
            if chunk:
                z.write(chunk)

    arch = glob.glob('ffmpeg*.tar.xz')[0]
    fullpath = extract_to_folder('ffmpeg', arch, z=False)
    out = '../linux'

    misc.Paths().convert_to_py(fullpath, out)

    linux = os.path.join(bin_path, 'linuxmod')
    shutil.copy('linux.py', linux)

print('All Done')