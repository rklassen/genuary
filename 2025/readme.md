# Genuary 2025 and experiments ex post

## Mar.2 Compositing
[Composited](./Mar.02/output/composite_2.png)

## Feb.18 Screentone
Separate image into chroma and luma, downsample luma and split into cmy cannels, blur, upres, and screen the cmy values. See March 2 for compositing.
[Screened cyan](./Feb.18/debug/step_06_screened_c.png)

## Feb.06 DCT Compression
Same as Feb.05 but with discrete cosine rather than fast fourier transform.
![Example frame](./Feb.06/output/frame_016.webp)

## Feb.05 Downsampling after FFT
Experimenting with results generated from performing FFT on the input image, manipulating the FFT output values, then performing. 

The narrowest question answered in this case is what results from performing a mipmap operation on the post-FFT values, excluding a margin on the perimeter of varying width.

More broadly, the question is (1) whether tranformations on raw FFT output are intuitive, 

## Jan.31 pixel sorting
[Video](./Jan.31/2025jan31.mp4)
![Desk](./Jan.31/output/2025jan31.gif) 
![Neon Wang](./Jan.31/output/2025jan31-neonuv.gif)

## Jan.22 gradients only
Nihilism compression algorithm
![Final Result Trashcore galaxy egg](./Jan.22/galaxy_egg_f.webp)

## Experiment 2. YCbCr
Split into YCbCr components, downsample chroma at 1/4 or 1/8 the resolution of luma. Reduce each nominal block size using nihilism algorithm.
[Video](./Jan.22/output_img/0001-0126.mp4)
![Color error](./Jan.22/output_img/test closeup.jpg)

## Experiment 1. Compress rgb channels separately.
Individual RGB gradients. ![rgb](./Jan.22/output_img/components-ethan.png). Compared with experiment zero, the compression ratio and visual quality are both worse.

### Experiment 0. Compress each block into min max rgb value and location.
Block size 8: ![Block size 8](./Jan.22/output_img/rgb_block_size_08.png)
Block size 16: ![Block size 16](./Jan.22/output_img/rgb_block_size_16.png)
Block size 32: ![Block size 32](./Jan.22/output_img/rgb_block_size_32.png)
Animated block size: ![Animated](./Jan.22/output_img/2025jan22_nihilism.gif)

# Jan 16 Generative Palette
Randomly generated palette from earth, jewel, neon, pastel saturation-luma ranges. Concise hsl_to_rgb fn.

# Jan 14 Black and white only
Animated screentone of an approximate EKG curve.
![Frame 0](./Jan.14/2025jan14.png)
[Video](./Jan.14/2025jan14.mp4)

# Jan.13 Triangles
## 2D
![jan13-2d](./Jan.13/2d/2025jan13.png)
## 3D
![jan13-3d](./Jan.13/3d/jan.13.palm.webp)

