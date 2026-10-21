These are 64x64 tiles used by the ROM as graphics. You can edit them with GIMP or something.

The .raw files are 64x64 1bpp which you can open in GIMP with the following parameters (anything not mentioned just leave default (probably doesn't matter)):
- (in the file open dialog select "raw image data" as the file type)
- Pixel format: B&W 1 bit
- Width: 64
- Height: 64

Some may also have source PNGs, you should probably open those instead if they exist and then update the 1bpp .raw

To export a 1bpp raw in GIMP:
- (seems) you can't. Try imagemagick: `magick sample.png-threshold 50% -negate MONO:sample.raw` or with dithering: `magick sample.png -dither FloydSteinberg -colors 2 -negate MONO:sample.raw`
