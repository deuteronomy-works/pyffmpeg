# pyffmpeg    ![Travis (.org)](https://img.shields.io/travis/deuteronomy-works/pyffmpeg/build-linux?label=Linux&logo=linux&logoColor=white&style=for-the-badge)  ![Travis (.org)](https://img.shields.io/travis/deuteronomy-works/pyffmpeg/build-darwin?label=MacOs&logo=apple&style=for-the-badge)  ![Travis (.org)](https://img.shields.io/travis/deuteronomy-works/pyffmpeg/build-windows?label=Windows&logo=windows&style=for-the-badge)  [![Downloads](https://static.pepy.tech/personalized-badge/pyffmpeg?period=month&units=international_system&left_color=brightgreen&right_color=black&left_text=Downloads)](https://pepy.tech/project/pyffmpeg)


FFmpeg wrapper for python. It uses the most up-to-date FFmpeg binary to provide both FFmpeg and FFprobe functionality. So you can kill two birds with one stone.

The beautiful thing about this is that it comes with it's own FFmpeg executable. It is compressed, making it the smallest one you can find. Becuase it's cross-platform and python 3, it is the only option available for building cross-platform apps with ffmpeg in python.

## FFmpeg Version
Uses current FFmpeg version

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
NB: The above digits are just for illustration purposes.


## Wiki
The wiki can be located [here](https://github.com/deuteronomy-works/pyffmpeg/wiki)


## Contributing
Please read [Contributing](https://github.com/deuteronomy-works/pyffmpeg/wiki/How-to-Contribute)

## Legal
This library uses prebuilt binaries of <a href=http://ffmpeg.org>FFmpeg</a> licensed under the <a href=http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html>LGPLv2.1</a> and can be downloaded via the following links:
  * Mac - <a href="https://evermeet.cx/ffmpeg/">here</a>
  * Linux - <a href="https://johnvansickle.com/ffmpeg/">here</a>
  * Windows - <a href="https://www.gyan.dev/ffmpeg/builds/">here</a>
