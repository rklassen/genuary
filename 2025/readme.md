# Genuary 2025 and experiments ex post
## May.20 SVG Generator
Creates procedural SVG graphics using Go, generates septagons and other geometric shapes with animation support and MP4 export.

## May.05 Gradient Triangles
Generates triangular patterns with cubic falloff gradients and noise. Creates smooth intensity transitions with random variation.

## Mar.12 WebP Converter
Simple Go utility for converting PNG images to WebP format using lossless compression. Demonstrates basic image format conversion.

## Mar.11 DCT Animation
Animates DCT frequency filtering effects on images, creating GIF output. Continues the DCT exploration series with motion graphics.

## Mar.10 DCT Aspect Ratios
Explores DCT compression at different aspect ratios (2:1, 3:1, 4:1). Generates multiple video outputs showing compression artifacts.

## Mar.09 DCT Iteration
Second iteration of DCT compression experiments, refining the frequency domain manipulation approach from Mar.08.

## Mar.08 DCT Frequency Filtering
Performs 2D DCT on YCbCr images, zeros lower frequencies, then applies inverse DCT. Explores frequency domain image manipulation.

## Mar.2 Compositing
Combines multiple processed image layers (chroma, luma, CMY channels) to create a final composited result, demonstrating advanced image blending techniques.
![Composited](./Mar.02/output/composite_2.png)

## Feb.18 Screentone
Separates image into chroma and luma, downsamples luma, splits into CMY channels, blurs, upscales, and screens CMY values for texture. See March 2 for compositing.
Separate image into chroma and luma, downsample luma and split into cmy cannels, blur, upres, and screen the cmy values. See March 2 for compositing.
![Screened cyan](./Feb.18/debug/step_06_screened_c.png)

## Feb.06 DCT Compression
Applies discrete cosine transform for image compression, similar to FFT but with DCT basis. Visualizes frame results.
Same as Feb.05 but with discrete cosine rather than fast fourier transform.
![Example frame](./Feb.06/output/frame_016.webp)

## Feb.05 Downsampling after FFT
Performs FFT on images, manipulates frequency domain, then inverse FFT to reconstruct. Explores mipmap and margin effects.
Experimenting with results generated from performing FFT on the input image, manipulating the FFT output values, then performing an inverse fft on the result to convert back to rgb.
![Example frame](./Feb.05/output/frame_016.webp)

The narrowest question answered in this case is what results from performing a mipmap operation on the post-FFT values, excluding a margin on the perimeter of varying width.

More broadly, the questions are (1) whether tranformations on raw FFT output are intuitive, which they do not seem to be, and (2) whether it can be nonetheless used to create interesting results.

## Jan.31 pixel sorting
Sorts image pixels by value to create visually striking effects and animations. Includes video and GIF results.
[Video](./Jan.31/2025jan31.mp4)

![Desk](./Jan.31/output/2025jan31.gif) 
![Neon Wang](./Jan.31/output/2025jan31-neonuv.gif)

## Jan.22 gradients only
Uses a nihilism compression algorithm to create gradient-based images and animations. Explores YCbCr and RGB block compression.
Nihilism compression algorithm
![Final Result Trashcore galaxy egg](./Jan.22/galaxy_egg_f.webp)

## Experiment 2. YCbCr
Splits images into YCbCr components, downsamples chroma, and compresses blocks using nihilism algorithm. Includes video and error visualization.
Split into YCbCr components, downsample chroma at 1/4 or 1/8 the resolution of luma. Reduce each nominal block size using nihilism algorithm.
[Video](./Jan.22/output_img/0001-0126.mp4)
![Color error](./Jan.22/output_img/test closeup.jpg)

## Experiment 1. Compress rgb channels separately.
Compresses each RGB channel independently, compares results to block-based compression. Shows individual gradients and quality tradeoffs.
Individual RGB gradients. ![rgb](./Jan.22/output_img/components-ethan.png). Compared with experiment zero, the compression ratio and visual quality are both worse.

### Experiment 0. Compress each block into min max rgb value and location.
Compresses blocks into min/max RGB values and locations. Demonstrates effect of block size and animated compression.
Block size 8: ![Block size 8](./Jan.22/output_img/rgb_block_size_08.png)
Block size 16: ![Block size 16](./Jan.22/output_img/rgb_block_size_16.png)
Block size 32: ![Block size 32](./Jan.22/output_img/rgb_block_size_32.png)
Animated block size: ![Animated](./Jan.22/output_img/2025jan22_nihilism.gif)

# Jan 16 Generative Palette
Generates random color palettes from earth, jewel, neon, and pastel ranges using concise HSL-to-RGB conversion.
Randomly generated palette from earth, jewel, neon, pastel saturation-luma ranges. Concise hsl_to_rgb fn.

# Jan 14 Black and white only
Creates animated screentone of an EKG curve using only black and white. Includes frame and video output.
Animated screentone of an approximate EKG curve.
![Frame 0](./Jan.14/2025jan14.png)
[Video](./Jan.14/2025jan14.mp4)

# Jan.13 Triangles
Generates triangle-based images in 2D and 3D. Includes PNG and WebP visualizations.
## 2D
![jan13-2d](./Jan.13/2d/2025jan13.png)
## 3D
![jan13-3d](./Jan.13/3d/jan.13.palm.webp)

