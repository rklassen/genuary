# Genuary 2025 - July 11
![WIP](./wip.webp)
_The error in hue is not intentional, it is _the_ next step in the devlog._
Lossy image compression using a build-time constant curve function with runtime-constant curve parameters, where each uncompressed input value in rgb or other three-component format is reduced to a single scalar `t`, a unorm or float, that represents that color's position on the curve. In this implementation, the curve is encoded in cylindrical HLS space where hue is angular, lightness is radial, and s is vertical.

[Example usage and details can be found in `example.md`](./example.md)

## Autopilot Description

This is a working version of a curve3d-based image palette remapper. It uses a 3D parametric curve to generate a palette, then maps each pixel of an input image to the closest color on the curve using a perceptual error function. The result is saved as a new image. The code is modular and ready for further experimentation.

## Devlog
Newest on top
Date Newest on Top | Commit | Action
--- | --- | ---
Scope Rapture | -- | Write an outer-loop genetic evolution algorithm that looks analyses the curve palette, input image, generates histograms of each for hue sat lum r g and b, looking for areas with high density and low density in the input image, generating curves that fit those.
Ultimate step | -- | Define generator-evaluator functions and write the meta-loop which generates generators. 
Penultimate step | -- | Revise the build-time constant curve function to handle min-z, max-z, and a single curve parameter that permits concentration of points on the low or high end of the range. Simplify constant where possible, phase of oscilation possibly. Finalize externally variable curve parameters; after this commit, serialization will be stable.
Next step | -- | Fix error(s) in round-trip color conversions, one or more points in rgb -> hls -> cylindrical -> hls -> rgb. Evident in variance in hue particularly when comparing before-and-after versions of the color palette.
2025 0713 | 27a5330b603d30917a665a7c8fcbb055979b94b7 | Colorspace operations, additional view generators
2025 0712 | 2199cdd4ab1be5bf5f248bd6f9986f0f11b4567d | Functionally complete, structural improvements
2025 0712 | d6f0affc8b41c845d0ae337ef28e3a4f6be77842 | Curve algo improvements
2025 0712 | d4ebeae5b0a3f2430cc8605da3a948d6b8676ad1 | Structurally complete, prototype best fit
2025 0711 | a2325a6146225214dbecc51f4c7eba57cf2122bb | Blender mockup, rust template

## Human Notes

### Finding palette curve - high cost

Computational time to minimize error in the uncompressed rgb (3D) value to 3d curve map process is very high but is computed once per palette. Palettes once composed are typically usable over multiple builds, multiple runtimes per build.

### Mapping image to palette - very very low

First iteration involves a naive, exhaustive search through points and discards all but the one with minimum error. Running acceptably fast. There are obvious but not critical performance improvements.
The error function is the most important part of the best fit algorithm and emcompasses volatile logic.
At present the logic will be serialized as pseudocode by human execution into the curve parameter and image md that gets saved with the image.

### Lookup from palette - trivial

CPU: precache palette array as rgb values
GPU: compute per-pixel using the curve equation as an hlsl function that reads the palette parameters from a uniform buffer.

## Project Structure

```
/ (root)
├── Cargo.toml
├── src/
│   ├── main.rs
│   ├── palettewheel.rs
│   └── models/
│       ├── mod.rs
│       ├── palettecurve.rs
│       ├── imagetovec.rs
│       └── imagetofile.rs
├── _input/
├── _output/
```

## Running the Project

```bash
# Build and run the project
cargo run

# Check for compile errors without producing an executable
cargo check

# Build in release mode
cargo build --release
```

[ _fin_ ]