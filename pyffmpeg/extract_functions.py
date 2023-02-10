# Created on 30th April, 2021
# Each function must return a list.
# the string should be in the format; key: value
# all functions must also be put in the FUNC_LIST
import re
import logging


logger = logging.getLogger('pyggmpeg.extract_functions')

# video functions

def _codec_name(line):
    logger.info('Inside _codec_name')
    if 'Video:' in line:
        cod = re.findall(r'Video: .*? ', line)[0]
        if cod.endswith(', '):
            cod = cod[:-2]
        name = cod.split(':')[1].strip()
        name_string = 'codec: ' + name
    else:
        return []

    return [name_string]


def _data_rate(line):
    logger.info('Inside _data_rate')
    dr = re.findall(r', \d+ [a-zA-Z]+/s', line)
    if dr:
        dr = dr[0].split(', ')[1]
        dr_string = 'data_rate: ' + dr
    else:
        return []

    return [dr_string]


def _dimensions(line):
    logger.info("Inside _dimensions")
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
    logger.info('Inside _fps')
    if 'fps' in line:
        fps = re.findall(r'\d+.?\d* fps', line)[0].split(' fps')[0]
        fps_str = 'fps: '+fps
    else:
        return []

    return [fps_str]


def _tbc(line):
    logger.info("Inside _tbc")
    if 'tbc' in line:
        tbc = re.findall(r'\d+.?\d* tbc', line)[0].split(' tbc')[0]
        tbc_str = 'tbc: ' + tbc
    else:
        return []

    return [tbc_str]


def _tbn(line):
    logger.info('Inside _tbn')
    if 'tbn' in line:
        tbn = re.findall(r'\d+.?\d* tbn', line)[0].split(' tbn')[0]
        tbn_str = 'tbn: ' + tbn
    else:
        return []

    return [tbn_str]


def _tbr(line):
    logger.info("Inside _tbr")
    if 'tbr' in line:
        tbr = re.findall(r'\d+.?\d* tbr', line)[0].split(' tbr')[0]
        tbr_str = 'tbr: ' + tbr
    else:
        return []

    return [tbr_str]


# audio functions

def _audio_codec_name(line):
    logger.info('Inside _audio_codec_name')
    if 'Audio:' in line:
        cod = re.findall(r'Audio: .*? ', line)[0]
        if cod.endswith(', '):
            cod = cod[:-2]
        name = cod.split(':')[1].strip()
        name_string = 'codec: ' + name
    else:
        return []

    return [name_string]


def _bit_rate(line):
    logger.info('Inside _bit_rate')
    bt = re.findall(r', \d+ [a-zA-Z]+/s', line)
    if bt:
        bt = bt[0].split(', ')[1]
        bt_string = 'bitrate: ' + bt
    else:
        return []

    return [bt_string]


def _channels(line):
    logger.info("Inside _channels")
    ch_string = 'channels: '
    if 'stereo' in line:
        ch_string += 'stereo'
    else:
        ch_string += 'mono'

    return [ch_string]


def _sample_rate(line):
    logger.info("Inside _sample_rate")
    sr = re.findall(r', \d+ Hz', line)
    if sr:
        sr = sr[0].split(', ')[1]
        sr_string = 'sample_rate: ' + sr
    else:
        return []

    return [sr_string]


AUDIO_FUNC_LIST = [_audio_codec_name, _bit_rate, _channels, _sample_rate]
VIDEO_FUNC_LIST = [
    _codec_name, _data_rate, _dimensions, _fps, _tbc, _tbn, _tbr]
