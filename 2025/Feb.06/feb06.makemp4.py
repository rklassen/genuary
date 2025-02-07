import os
import cv2


PROGRESS_BAR_WIDTH = 32
output_path = '2025/Feb.06/feb06.mp4'
frames_path = '2025/Feb.06/frames'

# region init
frame_files = sorted([os.path.join(frames_path, f) 
                      for f in os.listdir(frames_path) if f.endswith('.webp')])
if not frame_files:
    raise ValueError(f'No .webp files found in {frames_path}.')

frame = cv2.imread(frame_files[0])
height, width, layers = frame.shape
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(output_path, fourcc, 24, (width, height))

def print_progress_bar(prefix: str, progress: int, frame_count: int):
    progress = (progress + 1) / frame_count
    filled_length = int(PROGRESS_BAR_WIDTH * progress)
    bar = '.' * filled_length + ' ' * (PROGRESS_BAR_WIDTH - filled_length)
    print(f'{prefix} [ {bar} ] {int(progress * 100)}%', end='\r')
# endregion init

# region compile
for loop_index in range(2): # ping pong frames twice
    
    # Ascending order
    for frame_index, frame_file in enumerate(frame_files):
        print_progress_bar(f'Loop {1+loop_index} ascending ', frame_index, len(frame_files))
        frame = cv2.imread(frame_file)
        video.write(frame)
    print ('')
    
    # Descending order
    for frame_index, frame_file in enumerate(reversed(frame_files)):
        print_progress_bar(f'Loop {1+loop_index} descending', frame_index, len(frame_files))
        frame = cv2.imread(frame_file)
        video.write(frame)
    print ('')

video.release()
#endregion compile