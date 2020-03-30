import os
from platform import system
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

def test_get_ffmpeg_bin():

    if system() == 'Windows':
        fol = 'win32\\ffmpeg.exe'
    elif system == 'linux':
        fol = 'linux/ffmpeg'
    else:
        fol = 'darwin/ffmpeg'
    
    cwd = os.path.dirname(__file__)
    f_path = os.path.join(cwd, 'pyffmpeg', '.', 'static', 'bin', fol)
    bin_path = FFmpeg().get_ffmpeg_bin()
    print('bin: ', bin_path)
    assert f_path == bin_path

def test_options():

    opt = ['-i', 'H:\\GitHub\\pyffmpeg\\_test\\f.mp3',
           'H:\\GitHub\\pyffmpeg\\_test\\f.wav']
    a = FFmpeg()
    ret = a.options(opt)
    assert b'' == ret
