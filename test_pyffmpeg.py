import pytest
from pyffmpeg import FFmpeg

def test_main():
    """
    """
    if FFmpeg():
        assert True

def test_convert():
    """
    """
    a = FFmpeg()
    i = 'H:\\GitHub\\pyffmpeg\\_test\\f.mp3'
    o = 'H:\\GitHub\\pyffmpeg\\_test\\f.wav'

    ret = a.convert(i, o)
    assert ret == o
