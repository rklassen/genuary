## image and curve info

| Image               | Dimension |
| ------------------- | --------- |
| Width               | 854       |
| Height              | 1280      |

| PaletteCurve        |     Value |
| ------------------- | --------- |
| Sample Points       | 255       |          
| Amplitude           |    0.5716 |           
| Amplitude Phase     |    2.2763 |           
| Oscillation         |    0.9581 |           
| Oscillation Phase   |    5.1980 |           
| Harmonic            |    1.4928 |           

## evaluator logic
The evaluator uses this function to determine
which randomly generated curve is a best fit.

Luckily copilot can transpile rust and pseudocode
apparently pseudocode is syntactically compatible with js

```js
function error(point, target):
    hue_error = {
        dot = point.xy.normalized 
            • target.xy.normalized
        abs (
            arcsin (
                dot.clamp(0,1)
            )
        ) / PI
    }
    lum_error = abs (
        point.xy.length - target.xy.length
    )
    sat_error = abs (
        point.z - target.z
    )

    return 1.0 * hue_error
        + 1.24 * lum_error
        + 0.64 * sat_error
```