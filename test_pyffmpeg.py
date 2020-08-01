import os
from platform import system
import pytest
from pyffmpeg import FFmpeg

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

    i = 'H:\\GitHub\\pyffmpeg\\_test\\f.mp3'
    o = 'H:\\GitHub\\pyffmpeg\\_test\\f.wav'

    a = FFmpeg()
    ret = a.convert(i, o)
    os.remove(o)
    assert ret == o

def test_get_ffmpeg_bin():

    sys = system()
    if sys == 'Windows':
        folder = 'win32\\ffmpeg.exe'
    elif sys == 'linux':
        folder = 'linux/ffmpeg'
    else:
        folder = 'darwin/ffmpeg'
    
    cwd = os.path.dirname(__file__)
    f_path = os.path.join(cwd, 'pyffmpeg', '.', 'static', 'bin', folder)
    bin_path = FFmpeg().get_ffmpeg_bin()
    assert f_path == bin_path

def test_loglevel():
    ff = FFmpeg()
    ff.loglevel = 'fa'

    opt = ['-i', 'H:\\GitHub\\pyffmpeg\\_test\\f.mp3',
           'H:\\GitHub\\pyffmpeg\\_test\\f.wav']

    ff.options(opt)
    assert ff.loglevel != 'fa'

def test_options():

    opt = ['-i', 'H:\\GitHub\\pyffmpeg\\_test\\f.mp3',
           'H:\\GitHub\\pyffmpeg\\_test\\f.wav']
    a = FFmpeg()
    ret = a.options(opt)
    os.remove('H:\\GitHub\\pyffmpeg\\_test\\f.wav')
    assert b'' == ret
