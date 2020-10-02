import os
from platform import system
import pytest
from pyffmpeg import FFmpeg


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

    path = os.path.join(cwd, '_test')
    #i = os.path.join(path, 'f.mp3')
    o = os.path.join(path, 'f.wav')

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

    f_path = os.path.join(cwd, 'pyffmpeg', '.', 'static', 'bin', folder)
    bin_path = FFmpeg().get_ffmpeg_bin()
    assert f_path == bin_path

def test_loglevel():
    ff = FFmpeg()
    ff.loglevel = 'fa'

    path = os.path.join(cwd, '_test')
    #i = os.path.join(path, 'f.mp3')
    o = os.path.join(path, 'f.wav')

    opt = ['-i', i, o]

    ff.options(opt)
    assert ff.loglevel != 'fa'

def test_options():

    path = os.path.join(cwd, '_test')
    #i = os.path.join(path, 'f.mp3')
    o = os.path.join(path, 'f.wav')

    opt = ['-i', i, o]

    a = FFmpeg()
    ret = a.options(opt)
    os.remove(o)
    assert b'' == ret
