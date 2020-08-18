
from pyffmpeg import FFmpeg

ff = FFmpeg()
out = ff.convert('H:\\GitHub\\pyffmpeg\\_test\\f.mp3', 'H:\\GitHub\\pyffmpeg\\_test\\f.wav')
fps = ff.get_fps("H:/CS/practice/python/pyffmpeg subproces/vid.mp4")
print(out, fps)
