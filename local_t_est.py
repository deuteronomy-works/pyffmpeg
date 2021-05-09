import threading
from time import sleep
from pyffmpeg import FFmpeg


ff = FFmpeg()
ff.loglevel = 'info'


def tt():
    t_th = threading.Thread(target=ov)
    t_th.daemon = True
    t_th.start()
    qq()


def qq():
    sleep(3)
    print(ff._ffmpeg_instances)
    ff.quit('convert')


def ov():
    out = ff.convert('H:\\GitHub\\pyffmpeg\\_test\\quantum.mp4', 'H:\\GitHub\\pyffmpeg\\_test\\fa.mp3')
    print('done')
    if ff.error:
        if 'Output' in ff.error:
            assert True
        else:
            print(ff.error)
    else:
        assert True


fps = ff.get_fps("H:/CS/practice/python/pyffmpeg subproces/vid.mp4")
print(fps)

# tt()
