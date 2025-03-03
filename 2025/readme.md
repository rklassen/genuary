# Genuary 2025 and experiments ex post



## Feb.18 Screentone
Separate image into chroma and luma.
Step 1 ![Step 01 luma](./Feb.18/debug/step_01_y.png) Step 2 ![Step 02 chroma](./Feb.18/debug/step_02_chroma.png) ... Step 6 ![Screened cyan](./Feb.18/debug/step_06_screened_c.png) ![Screened magenta](./Feb.18/debug/step_06_screened_m.png) ![Screened yellow](./Feb.18/debug/step_06_screened_y.png)
Convert luma to cmy channels; downsample, blur, upres, and screen the cmy values. See March 2 for compositing.

## Feb.06 DCT Compression
Same as Feb.05 but with discrete cosine rather than fast fourier transform.
![Example frame](./Feb.06/output/frame_016.webp)

## Feb.05 Downsampling after FFT
Experimenting with results generated from performing FFT on the input image, manipulating the FFT output values, then performing. 

The narrowest question answered in this case is what results from performing a mipmap operation on the post-FFT values, excluding a margin on the perimeter of varying width.

More broadly, the question is (1) whether tranformations on raw FFT output are intuitive, 

## Jan.22 gradients only
Nihilism compression algorithm
![Final Result Trashcore galaxy egg](./Jan.22/galaxy_egg_f.webp)

## Experiment 2. YCbCr
Split into YCbCr components, downsample chroma at 1/4 or 1/8 the resolution of luma. Reduce each nominal block size using nihilism algorithm.
<video src="./Jan.22/output_img/0001-0126.mp4" controls="controls" style="max-width: 100%;">[Watch the video](./Jan.22/output_img/0001-0126.mp4)
</video>
![Color error](./Jan.22/output_img/test closeup.jpg)

## Experiment 1. Compress rgb channels separately.
Individual RGB gradients. ![rgb](./Jan.22/output_img/components-ethan.png). Compared with experiment zero, the compression ratio and visual quality are both worse.

### Experiment 0. Compress each block into min max rgb value and location.
Block size 8: ![Block size 8](./Jan.22/output_img/rgb_block_size_08.png)
Block size 16: ![Block size 16](./Jan.22/output_img/rgb_block_size_16.png)
Block size 32: ![Block size 32](./Jan.22/output_img/rgb_block_size_32.png)
Animated block size: ![Animated](./Jan.22/output_img/2025jan22_nihilism.gif)

## Jan.31 pixel sorting
<video src="./Jan.31/2025jan31.mp4" controls="controls" style="max-width: 100%;">[Watch the video](./Jan.31/2025jan31.mp4)</video>
![Desk](./Jan.31/output/2025jan31.gif) 
![Neon Wang](./Jan.31/output/2025jan31-neonuv.gif)
