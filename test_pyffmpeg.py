import os
# from platform import system
import pytest
from pyffmpeg import FFmpeg
from pyffmpeg.misc import Paths


cwd = os.path.dirname(__file__)

i = "https://raw.githubusercontent.com/"
i += "deuteronomy-works/pyffmpeg/master/tests/f.mp3"

TEST_FOLDER = "https://raw.githubusercontent.com/"
TEST_FOLDER += "deuteronomy-works/pyffmpeg/master/tests/"

# EASY_LEMON = os.path.join(
#    cwd, 'tests', 'Easy_Lemon_30_Second_-_Kevin_MacLeod.mp3')
EASY_LEMON = TEST_FOLDER + 'Easy_Lemon_30_Second_-_Kevin_MacLeod.mp3'

E_FLAT = TEST_FOLDER + "Ecossaise in E-flat - Kevin MacLeod.mp3"


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
    # ff.loglevel = 'info'
    print(f'in and out: {EASY_LEMON}, {out}')
    ff.convert(EASY_LEMON, out)
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
