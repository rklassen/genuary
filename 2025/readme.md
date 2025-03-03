# Genuary 2025 and experiments ex post

## Feb.06 DCT Compression
Follow up e
2025/Jan.31/2025jan31.mp4

## Feb.05 Downsampling after FFT
Experimenting with results generated from performing FFT on the input image, manipulating the FFT output values, then performing. 

The narrowest question answered in this case is what results from performing a mipmap operation on the post-FFT values, excluding a margin on the perimeter of varying width.

More broadly, the question is (1) whether tranformations on raw FFT output are intuitive, 

## Jan.22 gradients only
Nihilism compression algorithm
[Final Result Trashcore galaxy egg](.2025/Jan.22/galaxy_egg_f.webp)

## Experiment 2. YCbCr
Split into YCbCr components, downsample chroma at 1/4 or 1/8 the resolution of luma. Reduce each nominal block size using nihilism algorithm.
[Quantize levels] 2025/Jan.22/output_img/0001-0126.mp4
[Color error.](./Users/richardklassen/Developer/genuary/2025/Jan.22/output_img/test closeup.jpg)

## Experiment 1. Compress rgb channels separately.
Individual RGB gradients. [rgb](./2025/Jan.22/output_img/components-ethan.png). Compared with experiment zero, the compression ratio and visual quality are both worse.

### Experiment 0. Compress each block into min max rgb value and location.
Block size 8: [Block size 8](./2025/Jan.22/output_img/rgb_block_size_08.png)
Block size 16: [Block size 8](./2025/Jan.22/output_img/rgb_block_size_16.png)
Block size 32: [Block size 8](./2025/Jan.22/output_img/rgb_block_size_32.png)
Animated block size: [Animted](.2025/Jan.22/output_img/2025jan22_nihilism.gif)

## Jan.31 pixel sorting
[Final result](./2025/Jan.31/2025jan31.mp4)
[Desk](./2025/Jan.31/output/2025jan31.gif) 
[Neon Wang](./2025/Jan.31/output/2025jan31-neonuv.gif)
