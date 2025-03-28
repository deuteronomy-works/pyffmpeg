import os
import threading
from time import sleep
from pyffmpeg import FFmpeg


ff = FFmpeg()
ff.loglevel = 'info'
test_folder = os.path.abspath('./tests')


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
    input_file = os.path.join(test_folder, 'count down.mp4')
    output_file = os.path.join(test_folder, './outs/fa.mp3')

    #input_file = "https://raw.githubusercontent.com/deuteronomy-works/pyffmpeg/master/tests/countdown.mp4"
    out = ff.convert(input_file, output_file)
    # print(ff.error)

    if ff.error:
        if 'Output' in ff.error:
            assert True
        else:
            pass
            # print(ff.error)
    else:
        assert True


#fps = ff.get_fps("H:/CS/practice/python/pyffmpeg subproces/vid.mp4")
#print(fps)

ov()
# tt()
