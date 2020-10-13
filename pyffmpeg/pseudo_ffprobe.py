"""
To provide functionality only available from using ffprobe
without using ffprobe itself, but from ffmpeg log info
"""

import subprocess
from time import sleep
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
        print(self.raw_streams)
        for stream in self.raw_streams:
            if 'Video' in stream:
                # extract data
                # extract only fps for now
                func = self.video_extract_meths['fps']
                func(stream)
            self._extract_all(stream)

    def _extract_fps(self, stream):
        # Extract fps data from the stream
        fps_str = re.findall(r'\d+.?\d* fps', stream)[0].split(' fps')[0]
        self.fps = float(fps_str)

    def _extract_all(self, stdout):
        # pick only streams, all of them
        all_streams = stdout.split('Stream mapping')[0]
        # individual streams
        streams = all_streams.split('Stream')
        meta = []
        streamer = [['', [], []]]
        for x in range(len(streams)):
            if x == 0:
                meta = self._strip_meta(streams[x])
            else:
                streamer[0][x-1] = self._strip_meta(streams[x])

        print('meta: ', meta)
        print('stream: ', streamer)
        print('all: ', streamer[0][1])
        """print(main, '\n')
        print(zero, '\n')
        print(one, '\n')"""

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
        sleep(1)
        stdout, stderr = subP.communicate(input=b'q')

        os.unlink(out_file)

        if b'Videosss' in stdout:
            if not stderr:
                input_data = re.findall(r'Input .*?.*?.*?Stream mapping', str(stdout)[-2:1])[0]

                # take the streams data
                self.raw_streams = re.findall(r'Stream.*?.*?.*?handler_name.*?.*?.*?\\n', input_data)

            self._extract()
        else:
            self._extract_all(str(stdout, 'utf-*'))

    def _strip_meta(self, stdout):
        std = stdout.splitlines()
        meta_spaces = 0
        meta = []
        for line in std:
            a = re.findall(r'\s+[A-Za-z]', line)
            if a:
                a = a[0]
                if a[-1] == 'M':
                    meta_spaces = len(a[:-1])
                    continue
                if len(a[:-1]) <= meta_spaces and meta_spaces > 0:
                    break
                if meta_spaces > 0:
                    meta.append(line)

        return meta