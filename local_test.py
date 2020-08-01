
from pyffmpeg import FFmpeg

ff = FFmpeg()
out = ff.convert('H:\\GitHub\\pyffmpeg\\_test\\f.mp3', 'H:\\GitHub\\pyffmpeg\\_test\\f.wav')
print(out)
