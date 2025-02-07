# Feb 2 DCT test
`feb02.py` writes `result.webp`
Attempted to compress 2d image using 1D DCT's
    - one each in u and v directions
    - a third "error correction" DCT that runs along a diagonal

## Context
    - Jpeg, Webp and progeny use 2D DCT to use a variable bitcrunch per frequency, reducing the smallest waves to three bits while preserving full bit width for the large waves that have the greatest influence over the macro image.

    - Using 1D DCT's instead of 2D would of course reduce the compression rate further

    - But: using only two DCT's results in unacceptable loss of wave detail

    - How many 1D DCT's would it take to compress an image. Possibilities:
        - a 2D DCT has the same bit volume as 
        - Perform 1D DCT with a non-orthogonal ax(es) which may help normalize the error in one axis or the other and, if performed first with the orthogonal DCT's performed on only the resulting error, then this could normalize the error between the axes, i.e. would transfer error from one axis to the other.
        - This first attempt simply runs a DCT in three dimensions, u, v and and nonorthogonal "z" as described below.

## Thesis
    - while looking at a square DCT block, say 64 or 128 pixels wide,
    - perform a 1D DCT in the u and v axes
    - and a third DCT in the "z" axis which is defined in the uv plane at a diagonals parallel to x = y

## Attempt
    - limited by time. This uses naive DCT on three axes, does not perform 

## Result
![Resulting Image](result.webp)

## Next
1. Use numpy or scipy DCT to avoid likelihood of error in DCT formulae
2. Run u and v transforms on the _error_ resulting after the error "correction", non-orthogonal axes.