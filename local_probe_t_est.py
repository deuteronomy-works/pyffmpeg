import os
from pyffmpeg import FFprobe


test_folder = os.path.abspath('./tests/')
test_file = os.path.join(test_folder, 'loss_countdown.mkv')

f = FFprobe(test_file)
# ret = f.get_album_art('cover.png')


print(f.duration)
for x in f.metadata:
    print(x, '\n')
