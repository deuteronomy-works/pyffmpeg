import os
from platform import system
import pytest
from pyffmpeg import FFmpeg
from pyffmpeg.misc import Paths


cwd = os.path.dirname(__file__)
i = "https://raw.githubusercontent.com/deuteronomy-works/pyffmpeg/master/_test/f.mp3"


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
    o = os.path.join(path, 'f.wav')

    ff = FFmpeg()
    ff.convert(i, o)
    if os.path.exists(o):
        os.remove(o)
        assert True
    else:
        print(path)
        assert False

def test_get_ffmpeg_bin():

    home_path = Paths().load_ffmpeg_bin()
    bin_path = FFmpeg().get_ffmpeg_bin()
    assert home_path == bin_path

def test_loglevel():
    ff = FFmpeg()
    ff.loglevel = 'fa'

    path = Paths().home_path
    o = os.path.join(path, 'f.wav')

    opt = ['-i', i, o]

    ff.options(opt)
    assert ff.loglevel != 'fa'

def test_options():

    path = Paths().home_path
    o = os.path.join(path, 'f.wav')

    opt = ['-i', i, o]

    ff = FFmpeg()
    ff.options(opt)
    if os.path.exists(o):
        os.remove(o)
        assert True
    else:
        print(path)
        assert False
