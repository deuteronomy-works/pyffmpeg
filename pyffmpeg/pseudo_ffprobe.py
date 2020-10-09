"""
To provide functionality only available from using ffprobe
without using ffprobe itself, but from ffmpeg log info
"""

import subprocess
import re
import random
import os
from base64 import b64decode

from .misc import Paths, fix_splashes


class FFprobe():

    def __init__(self, file_name):

        self._ffmpeg = Paths().load_ffmpeg_bin()
        self.file_name = file_name

        # Video metadata
        self.fps = 0

        self.raw_streams = []
        self.video_extract_meths = {'fps': self._extract_fps}
        self.probe()

    def _extract(self):

        for stream in self.raw_streams:
            if 'Video' in stream:
                # extract data
                # extract only fps for now
                func = self.video_extract_meths['fps']
                func(stream)

    def _extract_fps(self, stream):
        # Extract fps data from the stream
        fps_str = re.findall(r'\d+.?\d* fps', stream)[0].split(' fps')[0]
        self.fps = float(fps_str)

    def probe(self):

        # randomize the filename to avoid overwrite prompt
        out_file = str(random.randrange(1, 10000000)) + '.mp3'

        commands = [self._ffmpeg, '-i', self.file_name, out_file]

        # start subprocess
        subP = subprocess.Popen(
            commands,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True)

        # break the operation
        stdout, stderr = subP.communicate(input=b'q')

        os.unlink(out_file)

        if not stderr:
            input_data = re.findall(r'Input .*?.*?.*?Stream mapping', str(stdout)[1:-2])[0]

            # take the streams data
            self.raw_streams = re.findall(r'Stream.*?.*?.*?handler_name.*?.*?.*?\\n', input_data)

        self._extract()
