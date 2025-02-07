import os,cv2
output_video = '2025/Feb.05/feb05.mp4'
frames_path = '2025/Feb.05/frames'


# init
frame_files = sorted([os.path.join(frames_path, f) for f in os.listdir(frames_path) if f.endswith('.webp')])
if not frame_files:
    raise ValueError("No .webp files found in the specified directory.")
frame = cv2.imread(frame_files[0])
height, width, layers = frame.shape
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(output_video, fourcc, 24, (width, height))

# ping pong frames twice
for _ in range(2): 
    # Ascending order
    for frame_file in frame_files:
        print(frame_file)
        frame = cv2.imread(frame_file)
        video.write(frame)
    
    # Descending order
    for frame_file in reversed(frame_files):
        print(frame_file)
        frame = cv2.imread(frame_file)
        video.write(frame)

video.release()