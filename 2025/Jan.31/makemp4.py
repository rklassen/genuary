import cv2
import os

frame_path = '/Users/richardklassen/Developer/genuary/2025/Jan.31/frames/'
start_frame, end_frame = 4, 252
step = 4
frames = [f'2025jan31_thresh{i}.png' for i in range(start_frame, end_frame + 1, step)]

first_frame = cv2.imread(os.path.join(frame_path, frames[0]))

height, width, layers = first_frame.shape
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter('/Users/richardklassen/Developer/genuary/2025/Jan.31/output.mp4', fourcc, 12, (width, height))
for frame in frames:
    img = cv2.imread(os.path.join(frame_path, frame))
    video.write(img)
video.release()
cv2.destroyAllWindows()