# Feb 18 - Screentone Part 1
[example.composite.webp](./example.composite.webp)

1. Split image into YCbCr components
2. Downsample CbCr into a 'flat luma' image. (i.e. the composite CbCr with median Y)
3. Split into cyan, magenta, and yellow components.*
4. Perform a 1px Blur to each component and upscale.
5. Generate screentone sdfs using cosine function.
6. Threshold the result in step 4 by the level in 5 to produce screened cyan magenta, and yellow channels.

*This gets confusing because both YCbCr and CMYK have a "Y" channel, which is the brightness in YCbCr and yellow in CMYK.

## 0. Original
[trashcore.galaxy.egg.webp](./input/trashcore.galaxy.egg.webp)

## 1. Split into YCbCr
[Cb](./debug/debug/step_01_cb.png) [Cr](./debug/debug/step_01_cr.png) [Y](./debug/debug/step_01_y.png)

## 2. Downsample and flatten chroma from CbCr
[Chroma](./debug/step_02_chroma.png)

## 3. Split flat chroma into CYMK
[cyan](./debug/step_03_cyan.png) [magenta](./debug/step_03_magenta.png) [yellow](./debug/step_03_yellow.png)

## 4. Blur each and upscale to original resolution
[yellow](./debug/step_04_blur_and_upscale_.png) [cyan](./debug/step_04_blur_and_upscale_cyan.png) [magenta](./debug/step_04_blur_and_upscale_magenta.png)

## 5. Generate screens at π/6 rotational increment
[screen 0](./debug/step_05_screentone_cyan.png) [screen π/6](./debug/step_05_screentone_magenta.png) [screen π/3](./debug/step_05_screentone_yellow.png)

## 6. Screen each processed cym channel
[screened cyan](./debug/step_06_screened_c.png) [screened magenta](./debug/step_06_screened_m.png) [screened yellow](./debug/step_06_screened_y.png)