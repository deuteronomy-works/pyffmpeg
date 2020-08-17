"""
To provide functionality only available from using ffprobe
without using ffprobe itself, but from ffmpeg log info
"""

import subprocess
import re
import random

class FFprobe():

    def __init__(self, file_name):
        self.file_name = file_name
        self.raw_streams = []
        self.video_extract_meths = {'fps': self._extract_fps}
        self.probe()

        # Video metadata
        self.fps = 0

    def _extract(self):

        for stream in self.raw_streams:
            if 'Video' in stream:
                # extract data
                # extract only fps for now
                func = self.video_extract_meths['fps']
                func(stream)

    def _extract_fps(self, stream):
        # Extract fps data from the stream
        fps_str = re.findall(r'\d+.?\d* fps', stream)[0].split(' fps')
        self.fps = float(fps_str)

    def probe(self):

        # randomize the filename to avoid overwrite prompt
        out_file = str(random.randrange(1, 10000000)) + '.mp3'

        commands = ['H:\\CS\\practice\\python\\pyffmpeg subproces\\ffmpeg.exe', '-i', self.file_name, out_file]

        # start subprocess
        subP = subprocess.Popen(
            commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            shell=True)

        # break the operation
        stdout, stderr = subP.communicate(input=b'q')

        if not stderr:
            input_data = re.findall(r'Input .*?.*?.*?Stream mapping', str(stdout)[1:-2])[0]

            # take the streams data
            self.raw_streams = re.findall(r'Stream.*?.*?.*?handler_name.*?.*?.*?\\n', input_data)

        self._extract()
        #print(self.raw_streams)


Probe("H:/CS/practice/python/pyffmpeg subproces/vv.mp4")
