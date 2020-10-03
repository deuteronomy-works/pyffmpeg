"""
To Provide miscellaneous function

"""

import os
from platform import system
from lzma import decompress
from base64 import b64decode, b64encode


def load_ffmpeg_bin():

    # Load OS specific ffmpeg executable
    os_name = system().lower()
    if os_name == 'windows':
        env_name = 'USERPROFILE'
        ffmpeg_ext = '.exe'
    else:
        env_name = 'HOME'
        ffmpeg_ext = ""

    bin_path = os.path.join(
        os.environ[env_name], '.pyffmpeg', 'bin')
    ffmpeg_file = os.path.join(
        bin_path, 'ffmpeg'+ffmpeg_ext)

    if not os.path.exists(ffmpeg_file):

        # load os specific ffmpeg bin data
        if os_name == 'windows':
            from .static.bin.win32 import win32
            b64 = win32.contents
        elif os_name == 'linux':
            from .static.bin.linux import linux
            b64 = linux.contents
        else:
            from .static.bin.darwin import darwin
            b64 = darwin.contents

        raw = b64decode(b64)
        decompressed = decompress(raw)
        # Create the folders
        if not os.path.exists(bin_path):
            os.makedirs(bin_path)
        # Finally create the ffmpeg file
        with open(ffmpeg_file, 'wb') as f_file:
            f_file.write(decompressed)

    return ffmpeg_file
