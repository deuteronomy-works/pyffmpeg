# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 15:07:19 2020
"""

import os
import shlex
import threading
import logging
from time import sleep
from typing import Optional
from subprocess import Popen, PIPE
# from platform import system
# from lzma import decompress
# from base64 import b64decode, b64encode

from .pseudo_ffprobe import FFprobe
from .misc import Paths, fix_splashes, SHELL, OS_NAME


logger = logging.getLogger('pyffmpeg')
logger.setLevel(logging.DEBUG)

log_file = os.path.join(Paths().home_path, 'pyffmpeg.log')
fh = logging.FileHandler(log_file)
ch = logging.StreamHandler()
fh.setLevel(logging.DEBUG)
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


class FFmpeg():

    """
    Provide methods for working with FFmpeg
    """

    def __init__(self, directory=".", enable_log: bool=True):
        """
        Init function
        """

        # Logger flag
        self.enable_log = enable_log

        if not self.enable_log:
            global log_file
            log_file = os.path.join(Paths(False).home_path, 'pyffmpeg.log')

        self.logger = logging.getLogger('pyffmpeg.FFmpeg')
        if self.enable_log:
            self.logger.info('FFmpeg Initialising')
        self.save_dir = directory
        if self.enable_log:
            self.logger.info(f"Save directory: {self.save_dir}")
        self.logger.info("Checking GitHub Activeness: True")
        self.overwrite = True
        self.create_folders = True
        self.loglevels = (
            'quiet', 'panic', 'fatal', 'error', 'warning',
            'info', 'verbose', 'debug', 'trace')
        self.loglevel = 'fatal'
        self._log_level_stmt = '-loglevel'
        if self.overwrite:
            self._over_write = '-y'
        else:
            self._over_write = '-n'

        # Progress
        self.report_progress = False
        self._in_duration: float = 0.0
        self._progress: int = 0
        self.onProgressChanged = self.progressChangeMock

        # instances are store according to function names
        self._ffmpeg_instances = {}
        if self.enable_log:
            self._ffmpeg_file = Paths(enable_log=True).load_ffmpeg_bin()
        else:
            self._ffmpeg_file = Paths(enable_log=False).load_ffmpeg_bin()
        if self.enable_log:
            self.logger.info(f"FFmpeg file: {self._ffmpeg_file}")
        self.error = ''

    def convert(self, input_file, output_file):

        """
        Converts and input file to the output file
        """
        if self.enable_log:
            self.logger.info('Inside convert function')
        if os.path.isabs(output_file):
            # absolute file
            out = output_file
        else:
            # not an absolute file
            out = os.path.join(self.save_dir, output_file)

        out_path = os.path.dirname(out)
        if not os.path.exists(out_path) and self.create_folders:
            os.makedirs(out_path)

        if self.enable_log:
            self.logger.info(f"Output file: {out}")

        inf = input_file.replace("\\", "/")
        if self.enable_log:
            self.logger.info(f"Input file: {inf}")

        if self.loglevel not in self.loglevels:
            msg = 'Warning: "{}" not an ffmpeg loglevel flag.' +\
             ' Using fatal instead'
            print(msg.format(self.loglevel))
            self.loglevel = 'fatal'

        options = [self._ffmpeg_file, "-loglevel", self.loglevel, self._over_write, "-i", inf, out]

        if self.enable_log:
            self.logger.info(f"shell: {SHELL}")

        if self.report_progress:
            f = FFprobe(inf)
            d = f.duration.replace(':', '')
            self._in_duration = float(d)
            self.monitor(out)

        try:
            outP = Popen(
                options, shell=False, stdin=PIPE,
                stdout=PIPE, stderr=PIPE
                )
            self.logger.error('did we')
            self._ffmpeg_instances['convert'] = outP
            self.logger.error('didn we')
            stderr = str(outP.stderr.read(), 'utf-8')
            self.logger.error('error should')

            print(stderr)
        except Exception as e:
            self.logger.error(e)
            stderr = e
            self.quit()

        if 'Output #0' not in stderr:
            lines = stderr.splitlines()
            if len(lines) > 0:
                self.error = "".join(lines)  # instead of lines[-1]
                self.error = "New error info: " + self.error
            else:
                self.error = "Error all: " + str(stderr)

            if self.enable_log:
                self.logger.error(self.error)
            raise Exception(self.error)
        else:
            self.error = ''
            if self.enable_log:
                self.logger.info('Conversion Done')
        return out

    def get_ffmpeg_bin(self):

        """
        Get the ffmpeg executable file. This is the fullpath to the
        binary distributed with pyffmpeg. There is only one at a time.
        """
        if self.enable_log:
            self.logger.info("Inside get_ffmpeg_bin")

        return self._ffmpeg_file

    def get_fps(self, input_file):
        """
        Returns the frame per second rate of an input file
        """
        if self.enable_log:
            self.logger.info("Inside get_fps")
        fprobe = FFprobe(input_file)
        fps = fprobe.fps
        return fps

    def monitor(self, fn: str):
        m_thread = threading.Thread(target=self._monitor, args=[fn])
        m_thread.daemon = True
        m_thread.start()

    def _monitor(self, fn: str):
        if self.enable_log:
            self.logger.info('Monitoring spirit started')
        sleep(1)
        dura = 0.0
        while dura < self._in_duration:
            try:
                f = FFprobe(fn)
                d = f.duration.replace(':', '')
                dura = float(d)
            except:
                dura = 0.0
            self.progress = dura / self._in_duration * 100
            sleep(0.1)

    def options(self, opts):

        """
        Allows user to pass any other command line options
        to the FFmpeg executable
        eg.: command line options of 'ffmpeg -i a.mp4 b.mp3'
        will be passed by user as: opts: '-i a.mp4 b.mp3'
        """
        if self.enable_log:
            self.logger.info("inside options")

        if isinstance(opts, list):
            if self.enable_log:
                self.logger.info('Options is a List')
            options = fix_splashes(opts)

            # Add overwrite variable
            options.insert(0, self._over_write)
            if self.loglevel not in self.loglevels:
                msg = 'Warning: "{}" not an ffmpeg loglevel flag.' +\
                 ' Using fatal instead'
                print(msg.format(self.loglevel))
                self.loglevel = 'fatal'

            options = ' '.join(options)
            options = ' '.join(['-loglevel', self.loglevel, options])

        else:
            if self.enable_log:
                self.logger.info('Options is a String')
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
        # Put into brackets if contain spaces
        if OS_NAME == "windows":
            _ffmpeg_file = '"' + self._ffmpeg_file + '"'
        else:
            _ffmpeg_file = self._ffmpeg_file
        
        self.logger.info(f'Using {_ffmpeg_file} as ffmpeg file')
        options = " ".join([_ffmpeg_file, options])
        self.logger.info(f"Options is: {options} as at now")

        if self.enable_log:
            self.logger.info(f"Shell: {SHELL}")

        if not SHELL:
            options = shlex.split(options, posix=False)

        try:
            out = Popen(options, shell=SHELL, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            self._ffmpeg_instances['options'] = out
            stderr = str(out.stderr.read(), 'utf-8')
        except:
            self.quit()

        if stderr and 'Output #0' not in stderr:
            lines = stderr.splitlines()
            if len(lines) > 0:
                self.error = lines[-1]
            else:
                self.error = ""
            self.logger.error(self.error)
            raise Exception(self.error)
        else:
            self.error = ''
            self.logger.info('Conversion Done')
        return True

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, percent):
        self._progress = int(percent)
        self.onProgressChanged(self._progress)

    def progressChangeMock(self, progress):
        pass

    def quit(self, function: Optional[str] = ''):

        """
        Allows for any running process of ffmpeg started by pyffmpeg
        to be terminated
        """
        if self.enable_log:
            self.logger.info('Inside Quit')

        if function:
            if self.enable_log:
                self.logger.info('There is a function for Quit: {function}')
            inst = self._ffmpeg_instances[function]
            output = inst.communicate(b'q')
        # Quit all instances
        else:
            for inst in self._ffmpeg_instances.values():
                output = inst.communicate(b'q')
