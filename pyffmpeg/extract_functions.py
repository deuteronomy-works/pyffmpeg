# Created on 30th April, 2021
# Each function must return a list.
# the string should be in the format; key: value
# all functions must also be put in the FUNC_LIST
import re


def _codec_name(line):
    if 'Video:' in line:
        cod = re.findall(r'Video: .*? ', line)[0]
        name = cod.split(':')[1].strip()
        name_string = 'codec: ' + name

    return [name_string]


def _dimensions(line):
    dim = re.findall(r', \d+x\d+ ', line)[0]
    if dim:
        dim = dim.split(', ')[1].strip()
        dim_string = 'dimensions: ' + dim

    sd = re.findall(r'\[SAR .*? DAR .*?\]', line)
    if sd:
        sd = sd[0].split(' ')
        sar_string = 'SAR: ' + sd[1]
        dar_string = 'DAR: ' + sd[3][:-1]

    return [dim_string, dar_string, sar_string]


def _fps(line):
    if 'fps' in line:
        fps = re.findall(r'\d+.?\d* fps', line)[0].split(' fps')[0]
        fps_str = 'fps: '+fps

    return [fps_str]


FUNC_LIST = [_codec_name, _dimensions, _fps]
