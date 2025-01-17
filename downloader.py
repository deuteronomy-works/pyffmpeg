import sys
import os
import shutil
import glob
import requests
import re

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
        pass
    shutil.unpack_archive(arch, extract_dir=cwd)
    print('done with unpack')
    fpath = f'**/{ffmpeg}'
    fname = glob.glob(fpath)[0]
    return os.path.join(cwd, fname)


def replace_setup_file_version():

    sta = '"Development Status :: 5 - Production/Stable"'
    bta = '"Development Status :: 4 - Beta"'

    # Version will be in format v2.4.2.20-beta.3-windows
    # or v2.4.2.20-windows
    ver = version.split('-')[0]
    ver = ver.replace('v', '')

    if 'beta' in version:
        beta = version.split('-')[1]
        beta = beta.split('beta.')[1]
        ver += f'b{beta}'

    with open('setup.py', 'r') as f:
        data = f.read()

    repl = re.compile("version='.*?[0-9]'")
    ver_str = f"version='{ver}'"
    data = repl.sub(ver_str, data)

    if 'beta' in version:
        data = data.replace(sta, bta)
    else:
        data = data.replace(bta, sta)

    with open('setup.py', 'w') as fw:
        fw.write(data)
    
    print('Done changing version type')


# Build wheel
if os_name == 'win32':
    # Download FFmpeg for Windows
    try:
        link = 'https://github.com/BtbN/FFmpeg-Builds/releases/download/'
        link += 'latest/ffmpeg-master-latest-win64-gpl.zip'
        resp = requests.get(link, stream=True)
        with open('ffmpeg-master-latest-win64-gpl.zip', 'wb') as z:
            for chunk in resp.iter_content(chunk_size=2048):
                if chunk:
                    z.write(chunk)
        print('done with download of winbin')

        # extract to folder
        arch = glob.glob('ffmpeg*.zip')[0]
        fullpath = extract_to_folder('ffmpeg.exe', arch, z=False)
        out = 'win32'

        misc.Paths().convert_to_py(fullpath, out)
        # copy all those contents to folder_name, skip exitsting
        win32 = os.path.join(bin_path, 'win32')
        # replace
        shutil.copy('win32.py', win32)

    except Exception as err:
        print(err)
        print(os.listdir(cwd))

elif os_name == 'darwin':
    try:
        link = 'https://evermeet.cx/ffmpeg/get/zip'
        resp = requests.get(link, stream=True)
        with open('ffmpeg.zip', 'wb') as z:
            for chunk in resp.iter_content(chunk_size=2048):
                if chunk:
                    z.write(chunk)

        arch = glob.glob('ffmpeg*.zip')[0]
        fullpath = extract_to_folder('ffmpeg',arch, z=False)
        out = 'darwin'

        misc.Paths().convert_to_py(fullpath, out)

        darwin = os.path.join(bin_path, 'darwin')
        shutil.copy('darwin.py', darwin)
    except Exception as err:
        print(err)
        print(os.listdir(cwd))

else:
    # Download FFmpeg for linux
    try:
        os_cmd = 'gh release download --repo'
        os_cmd += ' github.com/BtbN/FFmpeg-Builds --pattern "*latest-linux64-gpl.tar.xz"'
        os.system(os_cmd)

        arch = glob.glob('ffmpeg*.tar.xz')[0]
        fullpath = extract_to_folder('ffmpeg', arch, z=False)
        out = 'linux'

        misc.Paths().convert_to_py(fullpath, out)

        linux = os.path.join(bin_path, 'linuxmod')
        shutil.copy('linux.py', linux)
    except Exception as err:
        print(err)
        print(os.listdir(cwd))


# replace_setup_file_version()

print('All Done')
