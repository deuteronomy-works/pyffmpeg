# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 15:07:19 2020

"""

import os
from subprocess import check_output
from platform import system
from lzma import decompress
from base64 import b64decode

from .pseudo_ffprobe import FFprobe

# load os specific ffmpeg bin data
os_name = system().lower()
if os_name == 'windows':
    from .static.bin.win32 import win32
elif os_name == 'linux':
    from .static.bin.linux import linux
else:
    from .static.bin.darwin import darwin


class FFmpeg():


    """
    """


    def __init__(self, directory="."):

        self.save_dir = directory
        cwd = os.path.dirname(__file__)
        self.overwrite = True
        self.loglevels = (
            'quiet', 'panic', 'fatal', 'error', 'warning',
            'info', 'verbose', 'debug', 'trace')
        self.loglevel = 'fatal'
        self._log_level_stmt = '-loglevel'
        if self.overwrite:
            self._over_write = '-y'
        else:
            self._over_write = '-n'

        # Load OS specific ffmpeg executable
        if os_name == 'windows':
            self.path_to_ffmpeg = os.path.join(cwd, '.', 'static', 'bin',
                                               'win32')
            self._ffmpeg_file = os.path.join(self.path_to_ffmpeg,
                                             'ffmpeg.exe')
            b64 = win32.contents
        elif os_name == 'linux':
            self.path_to_ffmpeg = os.path.join(cwd, './static/bin/linux')
            self._ffmpeg_file = self.path_to_ffmpeg + '/ffmpeg'
            b64 = linux.contents
        elif os_name == 'darwin':
            self.path_to_ffmpeg = os.path.join(cwd, './static/bin/darwin')
            self._ffmpeg_file = self.path_to_ffmpeg + '/ffmpeg'
            b64 = darwin.contents
        else:
            b64 = ""

        if not os.path.exists(self._ffmpeg_file):
            raw = b64decode(b64)
            decompressed = decompress(raw)
            with open(self._ffmpeg_file, 'wb') as f:
                f.write(decompressed)

    def convert(self, input_file, output_file):

        """
        """

        if os.path.isabs(output_file):
            # absolute file
            o = output_file
        else:
            # not an absolute file
            o = os.path.join(self.save_dir, output_file)

        i = input_file.replace("\\", "/")

        if self.loglevel not in self.loglevels:
            msg = 'Warning: "{}" not an ffmpeg loglevel flag.' +\
            ' Using fatal instead'
            print(msg.format(self.loglevel))
            self.loglevel = 'fatal'

        check_output([
            self._ffmpeg_file, self._log_level_stmt, self.loglevel, self._over_write, '-i',
            i,
            o
            ], shell=True)
        return o

    def get_ffmpeg_bin(self):

        """
        Get the ffmpeg executable file. This is the fullpath to the
        binary distributed with pyffmpeg. There is only one at a time.
        """

        return self._ffmpeg_file

    def get_fps(self, input_file):
        fprobe = FFprobe(self.get_ffmpeg_bin, input_file)
        fps = fprobe.fps
        return fps

    def options(self, options):

        """
        """

        if type(options) == type([]):
            pass
        else:
            splits = options.split(' ')
            options = [item for item in splits]

        # Add ffmpeg and overwrite variable
        options.insert(0, self._over_write)
        if self.loglevel not in self.loglevels:
            msg = 'Warning: "{}" not an ffmpeg loglevel flag.' +\
            ' Using fatal instead'
            print(msg.format(self.loglevel))
            self.loglevel = 'fatal'

        if self.loglevel != 'fatal':
            options.insert(0, self.loglevel)
            options.insert(0, self._log_level_stmt)
        options.insert(0, self._ffmpeg_file)

        out = check_output(options, shell=True)
        return out
