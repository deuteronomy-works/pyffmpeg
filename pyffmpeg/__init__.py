# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 15:07:19 2020

"""

import os
from subprocess import check_output
from platform import system
from base64 import b64decode
if system() == 'Windows':
    from .static.bin.win32 import win32
elif system == 'linux':
    from .static.bin.linux import linux
else:
    from .static.bin.darwin import darwin

class FFmpeg():


    """
    """


    def __init__(self):

        cwd = os.path.dirname(__file__)

        # Load OS specific ffmpeg executable
        if system() == 'Windows':
            self.path_to_ffmpeg = os.path.join(cwd, './static/bin/win32')
            self.ffmpeg_file = self.path_to_ffmpeg + '\\ffmpeg.exe'
            b64 = win32.contents
        elif system == 'linux':
            self.path_to_ffmpeg = os.path.join(cwd, './static/bin/linux')
            self.ffmpeg_file = self.path_to_ffmpeg + '/ffmpeg'
            b64 = linux.contents
        elif system == 'darwin':
            self.path_to_ffmpeg = os.path.join(cwd, './static/bin/darwin')
            self.ffmpeg_file = self.path_to_ffmpeg + '/ffmpeg'
            b64 = darwin.contents
        else:
            b64 = ""

        raw = b64decode(b64)
        with open(self.ffmpeg_file, 'wb') as f:
            f.write(raw)

    def convert(self, input_file, output_file):

        i = input_file.replace("\\", "/")
        o = output_file

        if not os.path.exists(o):
            check_output([
                self.ffmpeg_file, '-i',
                i,
                o
                ], shell=True)

        return o
