# Feb 5 Fast fourier for image compression

Simple exploration of how relationship between FFT and the source or output image, particularly how error changes.

`feb05.fastfourier.py` splits the source into YCrCb and performs FFT on each image. Then mipmaps the center square of the image with a "safe margin" that animates from zero to n pixels. As the margin increases, the error converges towards zero.

## Result
![Resulting Image](output/transformed.webp)

## Next
Paint over FFT