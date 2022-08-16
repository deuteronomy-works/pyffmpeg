import pytest
from pyffmpeg import FFprobe
# test speed to make sure no convertion took place
# test file exist does not happen
TEST_FILES = {"tests/countdown.mp4", "tests/Easy_Lemon_30_Second_-_Kevin_MacLeod.mp3", "tests/Ecossaise in E-flat - Kevin MacLeod.mp3"}

def test_probe():
    for file in TEST_FILES:
        ffp = FFprobe(file)
        ffp.probe()


def test_album_art():
    pass
