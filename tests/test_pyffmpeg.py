import os
import requests
# from platform import system
import pytest
from pyffmpeg import FFmpeg
from pyffmpeg.misc import Paths


# are we offline?
try:
    resp = requests.get('https://google.com/')
    TEST_FOLDER = "http://raw.githubusercontent.com/"
    TEST_FOLDER += "deuteronomy-works/pyffmpeg/master/tests/"
except:
    TEST_FOLDER = os.path.join(os.path.abspath('.'), 'tests/')


cwd = os.path.dirname(__file__)


EASY_LEMON = TEST_FOLDER + 'Easy_Lemon_30_Second_-_Kevin_MacLeod.mp3'
E_FLAT = TEST_FOLDER + "Ecossaise in E-flat - Kevin MacLeod.mp3"
COUNTDOWN = TEST_FOLDER + 'countdown.mp4'


def test_save_directory():

    """
    Test to see if save directory is used
    """

    sav_dir = 'H:\\FakePath'
    ffmpeg = FFmpeg(sav_dir)
    if ffmpeg:
        assert ffmpeg.save_dir == sav_dir
    else:
        assert False


def test_convert():

    """
    """

    path = Paths().home_path
    out = os.path.join(path, 'f.wav')

    ff = FFmpeg()
    b_path = os.path.exists(ff.get_ffmpeg_bin())
    ff.loglevel = 'info'

    print(f'in and out: {COUNTDOWN} {path} {b_path}')

    ff.convert(COUNTDOWN, out)

    if ff.error:
        if 'Output' in ff.error:
            assert True
        else:
            print(ff.error)
            assert False
    else:
        assert True


def test_get_ffmpeg_bin():

    home_path = Paths().load_ffmpeg_bin()
    bin_path = FFmpeg().get_ffmpeg_bin()
    print('bin: ', bin_path)
    print('home: ', home_path)
    assert home_path == bin_path


def test_loglevel():
    ff = FFmpeg()
    ff.loglevel = 'fa'

    path = Paths().home_path
    o = os.path.join(path, 'f.wav')

    opt = ['-i', EASY_LEMON, o]

    ff.options(opt)
    assert ff.loglevel != 'fa'


def test_options():

    path = Paths().home_path
    o = os.path.join(path, 'f.wav')

    opt = ['-i', EASY_LEMON, o]

    ff = FFmpeg()
    print(f'in and out: {EASY_LEMON}, {o}')
    ff.options(opt)

    if ff.error:
        if 'Output' in ff.error:
            assert True
        else:
            print(ff.error)
            assert False
    else:
        assert True
