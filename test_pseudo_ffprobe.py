import pytest
import os
import requests
from collections import defaultdict
from pyffmpeg import FFprobe

# test speed to make sure no convertion took place
# test file exist does not happen


try:
    resp = requests.get('https://google.com')
    TEST_FOLDER = "https://raw.githubusercontent.com/"
    TEST_FOLDER += "deuteronomy-works/pyffmpeg/master/tests/"
except:
    TEST_FOLDER = os.path.join(os.path.abspath('.'), 'tests')


@pytest.mark.parametrize(
    'file_name,duration',
    [
        ("countdown.mp4", "00:00:04.37"),
        ('Easy_Lemon_30_Second_-_Kevin_MacLeod.mp3', "00:00:31.27"),
        ("Ecossaise in E-flat - Kevin MacLeod.mp3", "00:00:30.93")
    ])
def test_probe(file_name, duration):
    test_file = os.path.join(TEST_FOLDER, file_name)
    f = FFprobe(test_file)

    assert f.duration == duration


def test_album_art():
    pass

@pytest.mark.parametrize(
    'file_name',
    [
        ("countdown.mp4"),
    ]
)
def test_generate_tags(file_name):
    metadata_one = [
        '    major_brand     : mp42',
        '    minor_version   : 0',
        '    compatible_brands: isommp42',
        '    creation_time   : 2016-07-05T17:50:46.000000Z',
        '  Duration: 00:00:04.37',
        'start: 0.000000',
        'bitrate: 322 kb/s'
        ]
    metadata_two = [
        'codec: h264',
        'data_rate: 223 kb/s',
        'dimensions: 640x360',
        'DAR: 16:9',
        'SAR: 1:1',
        'fps: 29.97',
        'tbn: 30k',
        'tbr: 29.97',
        '      handler_name    : VideoHandler',
        '      vendor_id       : [0][0][0][0]',
        'codec: aac',
        'bitrate: 96 kb/s',
        'channels: stereo',
        'sample_rate: 44100 Hz',
        '      creation_time   : 2016-07-05T17:50:46.000000Z',
        '      handler_name    : IsoMedia File Produced by Google, 5-11-2011',
        '      vendor_id       : [0][0][0][0]',
        'Parsing a group of options: output url /dev/null.',
        'Opening an output file: /dev/null.',
        '[h264 @ 0x7f916e046480] nal_unit_type: 7(SPS), nal_ref_idc: 3',
        '[h264 @ 0x7f916e046480] nal_unit_type: 8(PPS), nal_ref_idc: 3'
        ]   
    tags_one = defaultdict(list,
        {
            'Duration': '00:00:04.37',
            'bitrate': '322 kb/s',
            'compatible_brands': 'isommp42',
            'creation_time': '2016-07-05T17:50:46.000000Z',
            'major_brand': 'mp42',
            'minor_version': '0',
            'start': '0.000000'
        })
    tags_two = defaultdict(list, 
        {
            'DAR': '16:9',
            'Opening an output file': '/dev/null.',
            'Parsing a group of options': 'output url /dev/null.',
            'SAR': '1:1',
            '[h264 @ 0x7f916e046480] nal_unit_type': '8(PPS), nal_ref_idc: '
                                                        '3',
            'bitrate': '96 kb/s',
            'channels': 'stereo',
            'codec': 'aac',
            'creation_time': '2016-07-05T17:50:46.000000Z',
            'data_rate': '223 kb/s',
            'dimensions': '640x360',
            'fps': '29.97',
            'handler_name': 'IsoMedia File Produced by Google, 5-11-2011',
            'sample_rate': '44100 Hz',
            'tbn': '30k',
            'tbr': '29.97',
            'vendor_id': '[0][0][0][0]'
        })    
    test_file = os.path.join(TEST_FOLDER, file_name)
    f = FFprobe(test_file)

    assert tags_one == f._generate_tags(metadata_one)
    assert tags_two == f._generate_tags(metadata_two)
