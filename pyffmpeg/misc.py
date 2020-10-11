"""
To Provide miscellaneous function
"""

import os
from platform import system
from lzma import decompress
from base64 import b64decode, b64encode


class Paths():

    def __init__(self):
        os_name = system().lower()
        if os_name == 'windows':
            env_name = 'USERPROFILE'
            self._ffmpeg_ext = '.exe'
        else:
            env_name = 'HOME'
            self._ffmpeg_ext = ""

        self.home_path = os.path.join(
            os.environ[env_name], '.pyffmpeg')
        self.bin_path = os.path.join(
            self.home_path, 'bin')
        # Create the folders
        if not os.path.exists(self.bin_path):
            os.makedirs(self.bin_path)
        self.ffmpeg_file = ''

    def load_ffmpeg_bin(self):

        # Load OS specific ffmpeg executable

        self.ffmpeg_file = os.path.join(
            self.bin_path, 'ffmpeg'+self._ffmpeg_ext)

        if not os.path.exists(self.ffmpeg_file):

            # load os specific ffmpeg bin data
            os_name = system().lower()
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
            # Finally create the ffmpeg file
            with open(self.ffmpeg_file, 'wb') as f_file:
                f_file.write(decompressed)

            # Do chmod on Unix
            if os_name != 'windows':
                os.system(f'chmod +x {self.ffmpeg_file}')

        return self.ffmpeg_file


def fix_splashes(options):
    if system().lower() == 'windows':
        new_opts = []
        for entry in options:
            fixed = entry
            if '/' in entry:
                fixing = entry.replace('/', '\\')
                fixed = fixing
            new_opts.append(fixed)
        return new_opts
    else:
        return options
