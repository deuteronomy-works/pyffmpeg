import pytest
from pyffmpeg import FFmpeg

def test_main():

    """
    """

    # Test to see if save directory is used
    sav_dir = 'H:\\Ulala'
    ffmpeg = FFmpeg(sav_dir)
    if ffmpeg:
        assert ffmpeg.save_dir == sav_dir
    else:
        assert False

def test_convert():

    """
    """

    i = 'H:\\GitHub\\pyffmpeg\\_test\\f.mp3'
    o = 'H:\\GitHub\\pyffmpeg\\_test\\f.wav'

    a = FFmpeg()
    ret = a.convert(i, o)
    assert ret == o

def test_options():

    opt = ['-i', 'H:\\GitHub\\pyffmpeg\\_test\\f.mp3', 'H:\\GitHub\\pyffmpeg\\_test\\f.wav']
    a = FFmpeg()
    ret = a.options(opt)
    assert b'' == ret
