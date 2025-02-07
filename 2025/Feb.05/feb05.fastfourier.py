import cv2
import numpy as np
from scipy.fft import fft2, ifft2
import os


image_path = '2025/Feb.06/source/palms3.webp'
image = cv2.imread(image_path)
ycrcb_image = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
y, cr, cb = cv2.split(ycrcb_image)

# Perform FFT on each component
y_fft = fft2(y)
cr_fft = fft2(cr)
cb_fft = fft2(cb)

# Set the FFT value to zero for every other column
# y_fft[:, ::2] = 0
# cr_fft[:, ::2] = 0
# cb_fft[:, ::2] = 0

# BLACKOUT A CIRCLE FROM CENTER TO RADIUS
# rows, cols = y.shape
# center_row, center_col = rows // 2, cols // 2
# radius = int(0.6 * cols)
# for r in range(rows):
#     for c in range(cols):
#         if (r - center_row) ** 2 + (c - center_col) ** 2 <= radius ** 2:
#             y_fft[r, c] = 0
#             cr_fft[r, c] = 0
#             cb_fft[r, c] = 0

def process_fft_and_save_image(y_fft, cr_fft, cb_fft, margin, output_path):
    rows, cols = y_fft.shape

    # in-place mipmap for all pixels except `margin` pixels from edge
    for r in range(margin, rows - margin):
        for c in range(margin, cols - margin):
            y_fft[r, c] = y_fft[r - 1, c]
            cr_fft[r, c] = cr_fft[r - 1, c]
            cb_fft[r, c] = cb_fft[r - 1, c]
        for c in range(margin + 1, cols - margin, 2):
            y_fft[r, c] = y_fft[r, c - 1]
            cr_fft[r, c] = cr_fft[r, c - 1]
            cb_fft[r, c] = cb_fft[r, c - 1]

    # Perform inverse FFT on each component
    y_ifft = np.abs(ifft2(y_fft))
    cr_ifft = np.abs(ifft2(cr_fft))
    cb_ifft = np.abs(ifft2(cb_fft))

    # Package the results
    merged_image = cv2.merge((y_ifft, cr_ifft, cb_ifft))
    rgb_image = cv2.cvtColor(merged_image.astype(np.uint8), cv2.COLOR_YCrCb2BGR)
    cv2.imwrite(output_path, rgb_image, [cv2.IMWRITE_WEBP_QUALITY, 80])

# note *frames/ in gitignore
output_dir = '2025/Feb.05/frames'
os.makedirs(output_dir, exist_ok=True)
for margin in range(64):
    output_path = os.path.join(output_dir, f'frame_{margin:03d}.webp')
    process_fft_and_save_image(y_fft.copy(), cr_fft.copy(), cb_fft.copy(), margin, output_path)