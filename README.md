# pyffmpeg    ![Travis (.org)](https://img.shields.io/travis/deuteronomy-works/pyffmpeg/build-linux?label=Linux&logo=linux&logoColor=white&style=for-the-badge)  ![Travis (.org)](https://img.shields.io/travis/deuteronomy-works/pyffmpeg/build-darwin?label=MacOs&logo=apple&style=for-the-badge)  ![Travis (.org)](https://img.shields.io/travis/deuteronomy-works/pyffmpeg/build-windows?label=Windows&logo=windows&style=for-the-badge)  [![Downloads](https://pepy.tech/badge/pyffmpeg)](https://pepy.tech/project/pyffmpeg)


FFmpeg wrapper for python. It uses FFmpeg binary to provide both FFmpeg and FFprobe functionality (FFprobe functionality includes `get_album_art`). So you can kill two birds with one stone.

The beautiful thing about it is that it comes with its own FFmpeg executable. It is compressed, making it the smallest you can find. And becuase its cross-platform and python 3, it is the only option available for building cross-platform apps with ffmpeg in python.

## FFmpeg Version
Uses current FFmpeg version 4.4

## Installation
    pip install pyffmpeg

## Usage
### FFmpeg
```python
from pyffmpeg import FFmpeg

inp = 'path/to/music_folder/f.mp4'
out = 'path/to/music_folder/f.mp3'

ff = FFmpeg()

output_file = ff.convert(inp, out)

print(output_file)

```

### FFprobe
Provides FFprobe functions and values


```python
from pyffmpeg import FFprobe

input_file = 'path/to/music.mp3'
fp = FFprobe(input_file)

print(fp.duration)
```
will print
```shell
> 00:04:32:32
```
NB: The above digits is just for illustration


## Wiki
The wiki can be located [here](https://github.com/deuteronomy-works/pyffmpeg/wiki)

## Legal
This library uses prebuilt binaries of <a href=http://ffmpeg.org>FFmpeg</a> licensed under the <a href=http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html>LGPLv2.1</a> and can be downloaded at the following links:
  * Mac - <a href="https://evermeet.cx/ffmpeg/">here</a>
  * Linux - <a href="https://johnvansickle.com/ffmpeg/">here</a>
  * Windows - <a href="https://www.gyan.dev/ffmpeg/builds/">here</a>
