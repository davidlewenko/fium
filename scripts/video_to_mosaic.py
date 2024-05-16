import cv2
import os
import numpy as np
from math import ceil, sqrt


train_or_test = 'test'

def count_mkv_files(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.mkv'):
                count += 1
    return count


def create_dirs(base_path, dir_names):
    for dir_name in dir_names:
        path = os.path.join(base_path, dir_name)
        os.makedirs(path, exist_ok=True)


def resolve_path(relative_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)


def extract_frames(video_path, frame_rate, max_frames=81):
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return []

    fps = video.get(cv2.CAP_PROP_FPS)
    interval = int(fps / frame_rate)
    frames = []
    count = 0
    success, image = video.read()

    while success and len(frames) < max_frames:
        if count % interval == 0:
            frames.append(image)
        success, image = video.read()
        count += 1

    video.release()
    if not frames:
        print(f"Error: No frames extracted from video {video_path}")
    return frames


def create_mosaic(frames, output_path):
    if not frames:
        print(f"Skipping mosaic creation for {output_path} due to no frames")
        return

    frame_count = len(frames)
    mosaic_dim = int(ceil(sqrt(frame_count)))
    frame_height, frame_width, _ = frames[0].shape
    mosaic_image = np.zeros((mosaic_dim * frame_height, mosaic_dim * frame_width, 3), dtype=np.uint8)

    for idx, frame in enumerate(frames):
        row = idx // mosaic_dim
        col = idx % mosaic_dim
        mosaic_image[row * frame_height:(row + 1) * frame_height, col * frame_width:(col + 1) * frame_width] = frame

    cv2.imwrite(output_path, mosaic_image)
    print(f"Mosaic created and saved at {output_path}")


def process_videos(input_dir, output_dir, frame_rate=2, max_frames=81):
    categories = ['MEFO', 'negativ']
    for category in categories:
        category_path = os.path.join(input_dir, category, f'initial_split/{train_or_test}')
        print(f"Processing category: {category}, path: {category_path}")

        if not os.path.exists(category_path):
            print(f"Directory not found: {category_path}")
            continue

        output_category_path = os.path.join(output_dir, category)
        os.makedirs(output_category_path, exist_ok=True)

        video_files = [f for f in os.listdir(category_path) if f.endswith('.mkv')]
        video_count = len(video_files)
        print(f"Total .mkv files to process in {category}: {video_count}")

        processed_count = 0
        for video_file in video_files:
            video_path = os.path.join(category_path, video_file)
            print(f"Processing video: {video_path}")

            frames = extract_frames(video_path, frame_rate, max_frames)
            if frames:
                mosaic_image_path = os.path.join(output_category_path, f"{os.path.splitext(video_file)[0]}.jpg")
                create_mosaic(frames, mosaic_image_path)
                processed_count += 1
            else:
                print(f"No frames extracted for video: {video_path}")

        print(f"Total videos processed in category {category}: {processed_count}")
        print(f"Total videos skipped in category {category}: {video_count - processed_count}")


# Example usage with relative paths
source_dir = resolve_path('../data/split_data')
#output_dir = resolve_path('../data/training_data')
output_dir = resolve_path('../data/testing_data')
process_videos(source_dir, output_dir)


mefo_dir = os.path.join(source_dir, '../MEFO/initial_split/test')
negativ_dir = os.path.join(source_dir, '../negativ/initial_split/test')

mefo_count = count_mkv_files(mefo_dir)
negativ_count = count_mkv_files(negativ_dir)

print(f"Total .mkv files in MEFO: {mefo_count}")
print(f"Total .mkv files in negativ: {negativ_count}")
