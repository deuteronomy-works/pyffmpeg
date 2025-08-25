"""
To Provide miscellaneous function
"""

import os
from platform import system
from lzma import decompress, compress
from base64 import b64decode, b64encode
import logging


logger = logging.getLogger('pyffmpeg.misc')


OS_NAME = system().lower()
logger.info(f"OS: {OS_NAME}")

if OS_NAME == 'linux':
    SHELL = False
else:
    SHELL = True


class Paths():
    """
    Provide access to paths used within pyffmpeg
    """

    def __init__(self, enable_log: bool=True):

        self.enable_log = enable_log

        if self.enable_log:
            self.logger = logging.getLogger('pyffmpeg.misc.Paths')
        self.os_name = OS_NAME
        if self.os_name == 'windows':
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
            if self.os_name != 'windows':
                os.system(f'chmod +rw {self.home_path}')
                os.system(f'chmod +rw {self.bin_path}')
        if self.enable_log:
            self.logger.info(f'bin folder: {self.bin_path}')
        self.ffmpeg_file = ''

    def load_ffmpeg_bin(self):

        if self.enable_log:
            self.logger.info('Inside load_ffmpeg_bin')

        # Load OS specific ffmpeg executable

        self.ffmpeg_file = os.path.join(
            self.bin_path, 'ffmpeg'+self._ffmpeg_ext)

        if not os.path.exists(self.ffmpeg_file):

            # load os specific ffmpeg bin data
            if self.os_name == 'windows':
                from .static.bin.win32 import win32
                b64 = win32.contents
            elif self.os_name == 'linux':
                from .static.bin.linuxmod import linux
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
            if self.os_name != 'windows':
                os.system(f'chmod +x {self.ffmpeg_file}')

        return self.ffmpeg_file

    @staticmethod
    def convert_to_py(fn: str, target: str):
        logger.info('Inside convert_to_py')

        with open(fn, 'rb') as f_file:
            raw = f_file.read()

        compressed = compress(raw)
        bs4 = b64encode(compressed)
        smtm = 'contents='+str(bs4)

        with open(target+'.py', 'w') as t_file:
            t_file.write(smtm)


def fix_splashes(options):
    """
    Make splashes synanymous irrespective of the OS
    """
    logger.info('Inside fix_splashes')
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


class ModifiedList(list):

    def __init__(self, other=[]):
        super().__init__(other)

    def __getitem__(self, index):
        length = super().__len__()

        if index >= length:
            raise Exception("Empty list")
        else:
            return super().__getitem__(index)
