# Feb 18 - Screentone continued


1. Split into YCbCr components
2. Downsample CbCr into a 'flat luma' image. (i.e. the composite CbCr with median Y)
3. Split into cyan, magenta, and yellow components.*
4. Perform a 1px Blur to each component and upscale. 
5. Generate screentone sdfs using cosine function.
6. Threshold the result in step 4 by the level in 5 to produce screened cyan magenta, and yellow channels.

*This gets confusing because both YCbCr and CMYK have a "Y" channel, which is the brightness in YCbCr and yellow in CMYK.