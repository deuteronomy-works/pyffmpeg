# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 15:07:19 2020

"""

import os
from subprocess import check_output
from platform import system
from lzma import decompress
from base64 import b64decode

from pyffmpeg.pseudo_ffprobe import FFprobe

# load os specific ffmpeg bin data
OS_NAME = system().lower()
if OS_NAME == 'windows':
    from pyffmpeg.static.bin.win32 import win32
elif OS_NAME == 'linux':
    from pyffmpeg.static.bin.linux import linux
else:
    from pyffmpeg.static.bin.darwin import darwin


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
        if OS_NAME == 'windows':
            self.path_to_ffmpeg = os.path.join(cwd,
            '.', 'static', 'bin', 'win32')
            self._ffmpeg_file = os.path.join(self.path_to_ffmpeg,
                                             'ffmpeg.exe')
            b64 = win32.contents
        elif OS_NAME == 'linux':
            self.path_to_ffmpeg = os.path.join(cwd,
            './static/bin/linux')
            self._ffmpeg_file = self.path_to_ffmpeg + '/ffmpeg'
            b64 = linux.contents
        elif OS_NAME == 'darwin':
            self.path_to_ffmpeg = os.path.join(cwd,
            './static/bin/darwin')
            self._ffmpeg_file = self.path_to_ffmpeg + '/ffmpeg'
            b64 = darwin.contents
        else:
            b64 = ""

        if not os.path.exists(self._ffmpeg_file):
            raw = b64decode(b64)
            decompressed = decompress(raw)
            # Create the folders
            if not os.path.exists(self.path_to_ffmpeg):
                os.makedirs(self.path_to_ffmpeg)
            # Finally create the ffmpeg file
            with open(self._ffmpeg_file, 'wb') as f_file:
                f_file.write(decompressed)

    def convert(self, input_file, output_file):

        """
        """

        if os.path.isabs(output_file):
            # absolute file
            out = output_file
        else:
            # not an absolute file
            out = os.path.join(self.save_dir, output_file)

        inf = input_file.replace("\\", "/")

        if self.loglevel not in self.loglevels:
            msg = 'Warning: "{}" not an ffmpeg loglevel flag.' +\
            ' Using fatal instead'
            print(msg.format(self.loglevel))
            self.loglevel = 'fatal'

        check_output([
            self._ffmpeg_file, self._log_level_stmt, self.loglevel,
            self._over_write, '-i', inf, out], shell=True)

        return out

    def get_ffmpeg_bin(self):

        """
        Get the ffmpeg executable file. This is the fullpath to the
        binary distributed with pyffmpeg. There is only one at a time.
        """

        return self._ffmpeg_file

    def get_fps(self, input_file):
        fprobe = FFprobe(self.get_ffmpeg_bin(), input_file)
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
