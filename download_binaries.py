from pathlib import Path
import sys
import shutil
import requests

from pyffmpeg import misc

root = Path(__file__).parent
bin_path = root / 'pyffmpeg/static/bin'
print (f"{bin_path = }")

# Download Qmlview archive for os
# extract to folder
# copy all those contents to folder_name, skipping the existing ones


def download(link: str) -> str:
    resp = requests.get(link, stream=True)
    if not Path(link).suffix:
        filename = "ffmpeg.zip"
    else:
        filename = Path(link).name
    with open(filename, 'wb') as z:
        for chunk in resp.iter_content(chunk_size=2048):
            if chunk:
                z.write(chunk)

    return next(root.glob(filename))

def extract_to_folder(ffmpeg_bin_name: str, arch: str, z=True) -> str:
    if z:
        pass
    shutil.unpack_archive(arch, extract_dir=root)
    print('done with unpack')
    return next(root.rglob(ffmpeg_bin_name))


bin_name = 'ffmpeg'

if sys.platform == "win32":
    # Download FFmpeg for Windows
    link = 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip'
    out = out_folder= 'win32'
    bin_name = 'ffmpeg.exe'

  
elif sys.platform == "darwin":
    # Download FFmpeg for MacOS
    link = 'https://evermeet.cx/ffmpeg/get/zip'
    out = out_folder= 'darwin'

else:
    # Download FFmpeg for linux
    link = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"
    out = 'linux'
    out_folder = 'linuxmod'

try:
    arch = download(link)
    fullpath = extract_to_folder(bin_name, arch, z=False)
    misc.Paths().convert_to_py(fullpath, out)
    pyfile_dest = bin_path / out_folder
    shutil.copy(f'{out}.py', pyfile_dest)

except Exception as err:
    print(f"{err!r}")
    print(list(root.iterdir()))
    raise

print('All Done')
