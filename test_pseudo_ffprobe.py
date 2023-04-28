import pytest
import os
import requests
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
        ('"Ea-sy_Lemon_30_Second_-_Kevin_MacLeod.mp3"', "00:00:31.29"),
        ('"Ecossaise in E-flat - Kevin MacLeod.mp3"', "00:00:30.96")
    ])
def test_probe(file_name, duration):
    test_file = os.path.join(TEST_FOLDER, file_name)
    f = FFprobe(test_file)

    assert f.duration == duration


def test_album_art():
    pass
