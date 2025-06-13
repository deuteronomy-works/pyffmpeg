"""
To provide functionality only available from using ffprobe
without using ffprobe itself, but from ffmpeg log info
"""

import subprocess
from time import sleep
import re
import random
import os
import logging
from collections import defaultdict
# from base64 import b64decode

from .misc import Paths, SHELL, ModifiedList
from .extract_functions import VIDEO_FUNC_LIST, AUDIO_FUNC_LIST


logger = logging.getLogger('pyffmpeg.pseudo_ffprobe')


class FFprobe():
    """
    Provide methods for working with pseudo ffprobe
    which is ffmpeg's log file
    """

    def __init__(self, file_name=None):

        self.logger = logging.getLogger('pyffmpeg.pseudo_ffprobe.FFprobe')
        self.logger.info('FFprobe initialised')
        self.misc = Paths()
        self._ffmpeg = self.misc.load_ffmpeg_bin()
        self.logger.info(f'ffmpeg bin: {self._ffmpeg}')
        self.file_name = file_name
        self.overwrite = True
        if self.overwrite:
            self._over_write = '-y'
        else:
            self._over_write = '-n'

        # Metadata
        self.fps = 0
        self.duration = 0
        self.start = 0
        self.bitrate = 0
        self.type = ''
        self.metadata = ModifiedList([ModifiedList([]), {}])  # mock indeces
        self.other_metadata = {}
        self._other_metadata = []

        self.streams = [[[], []]]
        self.stream_heads = []
        self.raw_streams = []

        # extracting methods
        self.video_extract_meths = {'fps': self._extract_fps}
        self.video_head_extract_meths = []

        # error reports
        self.error = ''

        # START
        self.probe()

    def _expose(self):
        # Expose public functions
        self.logger.info('Inside expose')

        if len(self.metadata[0]) < 1:
            self.logger.info("No metadata")
            return

        if 'Duration' in self.metadata[-1]:
            self.duration = self.metadata[-1]['Duration']

        if 'bitrate' in self.metadata[-1]:
            self.bitrate = self.metadata[-1]['bitrate']

        if 'fps' in self.metadata[0][0]:
            self.fps = self.metadata[0][0]['fps']

        elif len(self.metadata[0]) > 1 and 'fps' in self.metadata[0][1]:
            self.fps = self.metadata[0][1]['fps']

    def _extract(self):
        self.logger.info('Inside extract')
        for stream in self.raw_streams:
            self._extract_all(stream)

    def _extract_fps(self, stream):
        self.logger.info('Inside _extract_fps')
        # Extract fps data from the stream
        fps_str = re.findall(r'\d+.?\d* fps', stream)[0].split(' fps')[0]
        self.fps = float(fps_str)

    def _extract_all(self, stdout):
        self.logger.info('Inside _extract_all')
        # pick only streams, all of them

        if 'misdetection possible' in stdout:
            print('File corrupt or codecs not available for the file')
            return

        all_streams = stdout.split('Stream mapping')[0]
        all_streams = all_streams.split('Input')

        if len(all_streams) < 2:
            # Error
            all_streams = all_streams[0]
            self.error = re.split(r'libpostproc .*?.*?.*?\n', all_streams)[-1]
            self.logger.error(self.error)
            raise Exception(self.error)
        else:
            del all_streams[0]
            if len(all_streams) > 1:
                print("Multiple input files found.\
                     However only one will be probed")
            all_streams = all_streams[0]
        # individual streams
        streams = all_streams.split('Stream')
        self.metadata[-1] = self._parse_input_meta(streams[0])

        tags = defaultdict(list)
        for x in range(1, len(streams)):
            if streams[x]:
                tags.update(self._parse_meta(streams[x]))

        if len(tags) > 0:
            self.metadata[0] = tags

        self._parse_other_meta()

        # then handle stream 0:0 so
        self._parse_stream_meta(self.stream_heads)

    def get_album_art(self, out_file=None):
        self.logger.info('Inside get_album_art')
        user_file = True
        if not out_file:
            # randomize the filename to avoid overwrite prompt
            out_file = str(random.randrange(1, 10000000)) + '.jpg'
            out_file = os.path.join(self.misc.home_path, out_file)
            user_file = False
        else:
            # make directory suplied by user, read and write
            dir_name = os.path.dirname(out_file)
            if self.misc.os_name != 'windows':
                os.system(f'chmod +rw {dir_name}')

        commands = f'{self._ffmpeg} {self._over_write}'
        commands += f' -i "{self.file_name}" -an'
        commands += f' -vcodec copy "{out_file}"'

        # start subprocess
        subP = subprocess.run(commands, capture_output=True)
        if subP.returncode == 0:
            if user_file:
                return True
            else:
                with open(out_file, 'rb') as out:
                    data = out.read()
                os.unlink(out_file)
                return data

    def _parse_meta(self, stream):
        self.logger.info('Inside _parse_meta')
        metadata = self._strip_meta(stream)
        tags = self._generate_tags(metadata)
        return tags

    def _parse_header(self, line):
        self.logger.info('Inside _parse_header')
        parsed = []

        if 'Video' in line:
            # extract data
            for func in VIDEO_FUNC_LIST:
                parsed.extend(func(line))

        elif 'Audio' in line:
            # extract audio data
            for func in AUDIO_FUNC_LIST:
                parsed.extend(func(line))

        return parsed

    def _parse_input_meta(self, stream):
        self.logger.info('Inside _parse_input_meta')
        metadata = self._strip_input_meta(stream)
        tags = self._generate_tags(metadata)
        return tags

    def _parse_other_meta(self):
        self.logger.info('Inside _parse_other_meta')
        for stream in self._other_metadata:
            items = stream.split(',')
            for each in items:
                data = each.split(":", 2)
                key = data[0].strip()
                value = data[1].strip()
                # there might be multiple
                if key == '' and len(data) > 2:
                    key = value
                    value = data[2].strip()
                self.other_metadata[key] = value

        # try to extract the known
        # Add more to it
        # and even move it to a function loop
        if 'Duration' in self.other_metadata:
            self.duration = self.other_metadata['Duration']
        elif 'start' in self.other_metadata:
            self.start = self.other_metadata['start']
        elif 'bitrate' in self.other_metadata:
            self.bitrate = self.other_metadata['bitrate']

    def _parse_stream_meta(self, stream):
        self.logger.info('Inside _parse_stream_meta')
        for stream in stream:
            infos = stream.split(': ')[-1]
            data = infos.split(', ')

            # try to extract the known
            # Add more to it
            for each in data:
                if '/s' in each:
                    self.bitrate = each
                # more should be added here
                elif each in ('mp3', 'mp4'):
                    self.type = each

    def probe(self):
        self.logger.info('Inside probe')
        self.logger.info(f'Probing file: "{self.file_name}"')

        # randomize the filename to avoid overwrite prompt

        commands = [
            self._ffmpeg, '-y', '-i',
            self.file_name, '-f',
            'null', os.devnull]

        self.logger.info(f"Issuing commads {str(commands)}")

        # start subprocess
        subP = subprocess.Popen(
            commands,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=False)

        # break the operation
        sleep(0.5)
        stdout, _ = subP.communicate(input='q')

        self._extract_all(stdout)

        # Expose publicly know var
        self._expose()

    def _strip_meta(self, stdout):
        self.logger.info('Inside _strip_meta')
        std = stdout.splitlines()

        # store in stream header
        header = self._parse_header(std[0])
        std.pop(0)

        meta = []
        for line in std:
            items = line.split(': ')
            if len(items) > 1 and items[1]:
                meta.append(line)

        return header + meta

    def _strip_input_meta(self, stdout):
        self.logger.info('Inside _strip_input_meta')
        # replace commas with '\r\n'
        stdout = stdout.replace(', ', '\r\n')
        std = stdout.splitlines()

        meta = []
        for line in std:
            items = line.split(': ')
            if len(items) > 1 and items[1]:
                meta.append(line)

        return meta

    def _generate_tags(self, metadata):
        prev_key = ''
        tags = defaultdict(list)

        for x in range(len(metadata)):
            line = metadata[x]
            data = line.split(":", 1)
            key = data[0].strip() 
            value = data[1].strip()
            # this might be a continuation, if not we add it to orphaned key list
            if key == '':
                if prev_key == '':
                    tags['unpaired_values'].append(value)
                else:
                    tags[prev_key].append("\\r\\n" + data[1].strip())
            else:
                tags[key] = value
                prev_key = key
        return tags