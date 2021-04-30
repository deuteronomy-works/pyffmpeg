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
    else:
        return []

    return [name_string]


def _data_rate(line):
    dr = re.findall(r', \d+ [a-zA-Z]+/s', line)
    if dr:
        dr = dr[0].split(', ')[1]
        dr_string = 'data_rate: ' + dr
    else:
        return []

    return [dr_string]


def _dimensions(line):
    dim = re.findall(r', \d+x\d+ ', line)
    if dim:
        dim = dim[0].split(', ')[1].strip()
        dim_string = 'dimensions: ' + dim
    else:
        return []

    sd = re.findall(r'\[SAR .*? DAR .*?\]', line)
    if sd:
        sd = sd[0].split(' ')
        sar_string = 'SAR: ' + sd[1]
        dar_string = 'DAR: ' + sd[3][:-1]
    else:
        return [dim_string]

    return [dim_string, dar_string, sar_string]


def _fps(line):
    if 'fps' in line:
        fps = re.findall(r'\d+.?\d* fps', line)[0].split(' fps')[0]
        fps_str = 'fps: '+fps
    else:
        return []

    return [fps_str]


def _tbc(line):
    if 'tbc' in line:
        tbc = re.findall(r'\d+.?\d* tbc', line)[0].split(' tbc')[0]
        tbc_str = 'tbc: '+ tbc
    else:
        return []

    return [tbc_str]


FUNC_LIST = [_codec_name, _data_rate, _dimensions, _fps, _tbc, _tbn, _tbr]
