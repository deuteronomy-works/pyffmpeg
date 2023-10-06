import os
import pprint
from pyffmpeg import FFprobe


test_folder = os.path.abspath('./tests/')
test_file = os.path.join(test_folder, 'Easy_Lemon_30_Second_-_Kevin_MacLeod.mp3')
# test_file = "G:\Entertainment\Movies\[PFM].Hacksaw.Ridge.2016.720p.BrRip.x265.HEVCBay.mkv"
#test_file = "G:\Entertainment\Movies\Interstellar (2014)\Interstellar.2014.720p.BluRay.x264.YIFY.mp4"
flv_file = os.path.join(test_folder, 'sample_960x400_ocean_with_audio.flv')

f = FFprobe(flv_file)
# ret = f.get_album_art('cover.png')


pprint.pprint(f.duration)
for x in f.metadata:
    print(x, '\n')

pprint.pprint(f.metadata)
pprint.pprint(f.metadata[0])
# print(f.metadata[0][0])
print("is codec flv1?")
pprint.pprint(f.metadata[0]['codec'] == 'flv1')