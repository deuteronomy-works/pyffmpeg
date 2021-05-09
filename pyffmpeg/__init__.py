# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 15:07:19 2020
"""

import os
from typing import Optional
from subprocess import Popen, PIPE, STDOUT
from platform import system
from lzma import decompress
from base64 import b64decode, b64encode

from .pseudo_ffprobe import FFprobe
from .misc import Paths, fix_splashes


class FFmpeg():


    """
    """


    def __init__(self, directory="."):

        self.save_dir = directory
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

        # instances are store according to function names
        self._ffmpeg_instances = {}
        self._ffmpeg_file = Paths().load_ffmpeg_bin()
        self.error = ''

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

        options = f"{self._ffmpeg_file} -loglevel {self.loglevel} "
        options += f"{self._over_write} -i {inf} {out}"
        outP = Popen(options, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        self._ffmpeg_instances['convert'] = outP
        self.error = str(outP.stderr.read(), 'utf-8')
        return out

    def get_ffmpeg_bin(self):

        """
        Get the ffmpeg executable file. This is the fullpath to the
        binary distributed with pyffmpeg. There is only one at a time.
        """

        return self._ffmpeg_file

    def get_fps(self, input_file):
        fprobe = FFprobe(input_file)
        fps = fprobe.fps
        return fps

    def options(self, opts):

        """
        """

        if isinstance(opts, list):
            options = fix_splashes(opts)

            # Add ffmpeg and overwrite variable
            options.insert(0, self._over_write)
            if self.loglevel not in self.loglevels:
                msg = 'Warning: "{}" not an ffmpeg loglevel flag.' +\
                 ' Using fatal instead'
                print(msg.format(self.loglevel))
                self.loglevel = 'fatal'

            options = ' '.join(options)
            options = ' '.join(['-loglevel', self.loglevel, options])

        else:
            options = opts

            # Add ffmpeg and overwrite variable

            # handle overwrite
            if self._over_write not in options:
                options = " ".join([self._over_write, options])

            # handle loglevel
            if self._log_level_stmt not in options:
                if self.loglevel not in self.loglevels:
                    msg = 'Warning: "{}" not an ffmpeg loglevel flag.' +\
                     ' Using fatal instead'
                    print(msg.format(self.loglevel))
                    self.loglevel = 'fatal'

                if self.loglevel != 'fatal':
                    options = " ".join(
                        [options])

        # add ffmpeg
        options = " ".join([self._ffmpeg_file, options])

        out = Popen(options, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        self._ffmpeg_instances['options'] = out
        self.error = str(out.stderr.read(), 'utf-8')
        return True

    def quit(self, function: Optional[str] = ''):
        if function:
            inst = self._ffmpeg_instances[function]
            output = inst.communicate(b'q')
        # Quit all instances
        else:
            for inst in self._ffmpeg_instances.values():
                output = inst.communicate(b'q')
                print('out: ', output)
