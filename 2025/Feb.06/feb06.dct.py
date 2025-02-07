import cv2
import numpy as np
from scipy.fft import dct, idct
from PIL import Image
import os

DCT_PATH = '2025/Feb.06/output/y-dct.webp'
IMG_PATH = '2025/Feb.06/output/transformed.webp'
PROGRESS_BAR_WIDTH = 32
FRAME_COUNT = 64
image_path = '2025/Feb.06/source/palms3.webp'

# load the image, split into y cr cb
image = cv2.imread(image_path)
ycrcb_image = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
y, cr, cb = cv2.split(ycrcb_image)

# Perform DCT on each component
y_dct = dct(dct(y.T, norm='ortho').T, norm='ortho')
cr_dct = dct(dct(cr.T, norm='ortho').T, norm='ortho')
cb_dct = dct(dct(cb.T, norm='ortho').T, norm='ortho')

def process_dct_and_save_image(y_dct, cr_dct, cb_dct, margin, output_path):
    rows, cols = y_dct.shape

    # in-place mipmap for all pixels except `margin` pixels from edge
    for r in range(margin, rows - margin):
        for c in range(margin + 1, cols - margin, 2):
            y_dct[r, c] = y_dct[r, c - 1]
            cr_dct[r, c] = cr_dct[r, c - 1]
            cb_dct[r, c] = cb_dct[r, c - 1]
        for c in range(margin, cols - margin):
            y_dct[r, c] = y_dct[r - 1, c]
            cr_dct[r, c] = cr_dct[r - 1, c]
            cb_dct[r, c] = cb_dct[r - 1, c]

    # Perform inverse DCT on each component
    y_idct = idct(idct(y_dct.T, norm='ortho').T, norm='ortho')
    cr_idct = idct(idct(cr_dct.T, norm='ortho').T, norm='ortho')
    cb_idct = idct(idct(cb_dct.T, norm='ortho').T, norm='ortho')

    # Package the results
    merged_image = cv2.merge((y_idct, cr_idct, cb_idct))
    rgb_image = cv2.cvtColor(merged_image.astype(np.uint8), cv2.COLOR_YCrCb2BGR)
    cv2.imwrite(output_path, rgb_image, [cv2.IMWRITE_WEBP_QUALITY, 80])

    # Save the third dct frame and corresponding output
    if margin == 3:
        y_idct_image = Image.fromarray(y_idct.astype(np.uint8))
        y_idct_image.save(DCT_PATH, 'WEBP', quality=80)
        cv2.imwrite(IMG_PATH, rgb_image, [cv2.IMWRITE_WEBP_QUALITY, 80])

# note *frames/ in gitignore
output_dir = '2025/Feb.06/frames'
os.makedirs(output_dir, exist_ok=True)
for margin in range(FRAME_COUNT):
    output_path = os.path.join(output_dir, f'frame_{margin:03d}.webp')
    process_dct_and_save_image(y_dct.copy(), cr_dct.copy(), cb_dct.copy(), margin, output_path)
    progress = (margin + 1) / FRAME_COUNT
    filled_length = int(PROGRESS_BAR_WIDTH * progress)
    bar = '.' * filled_length + ' ' * (PROGRESS_BAR_WIDTH - filled_length)
    print(f'[{bar}] {int(progress * 100)}%', end='\r')

print(f'\nAll {FRAME_COUNT} frames are complete.')