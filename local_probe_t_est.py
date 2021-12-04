from pyffmpeg import FFprobe

f = FFprobe("C:/Users/Ampofo/Videos/RECORDINGS/SignIn/o/2movie Audio Extracted.wav")
# ret = f.get_album_art('cover.png')


print(f.duration)
for x in f.metadata:
    print(x, '\n')
