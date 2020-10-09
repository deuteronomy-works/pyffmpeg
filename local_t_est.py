
from pyffmpeg import FFmpeg

ff = FFmpeg()
ff.loglevel = 'info'
out = ff.convert('H:\\GitHub\\pyffmpeg\\_test\\f.mp3', 'H:\\GitHub\\pyffmpeg\\_test\\f.wav')
if ff.error:
    if 'Output' in ff.error:
        assert True
    else:
        print(ff.error)
else:
    assert True
fps = ff.get_fps("H:/CS/practice/python/pyffmpeg subproces/vid.mp4")

