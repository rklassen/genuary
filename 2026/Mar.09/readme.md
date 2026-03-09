# Mar.09 (2026)

CMYK ordered dithering experiment with:
- 2x linear downsample
- 8x8 Morton threshold matrix per channel
- half-block row staggering inside each channel
- channel-to-channel phase staggering
- Gabor modulation before thresholding per channel

## Run

```powershell
python mar09_cmyk_morton_gabor.py input\*.jpg --output-dir output
```

Optional controls:
- `--gabor-strength` (default `0.18`)
- `--gabor-freq` (default `0.018`)
- `--gabor-sigma-scale` (default `0.03125` (1/32))



