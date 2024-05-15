import cv2
import os
import numpy as np
from math import ceil, sqrt


def create_dirs(base_path, dir_names):
    for dir_name in dir_names:
        path = os.path.join(base_path, dir_name)
        os.makedirs(path, exist_ok=True)


def resolve_path(relative_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)


def extract_frames(video_path, frame_rate, max_frames=81):
    video = cv2.VideoCapture(video_path)
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
    return frames


def create_mosaic(frames, output_path):
    if not frames:
        print(f"No frames extracted for {output_path}")
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
        category_path = os.path.join(input_dir, category, 'initial_split/test')
        print(f"Processing category: {category}, path: {category_path}")

        if not os.path.exists(category_path):
            print(f"Directory not found: {category_path}")
            continue

        output_category_path = os.path.join(output_dir, category)
        os.makedirs(output_category_path, exist_ok=True)

        for video_file in os.listdir(category_path):
            if video_file.endswith('.mkv'):
                video_path = os.path.join(category_path, video_file)
                print(f"Processing video: {video_path}")

                frames = extract_frames(video_path, frame_rate, max_frames)
                if frames:
                    mosaic_image_path = os.path.join(output_category_path, f"{os.path.splitext(video_file)[0]}.jpg")
                    create_mosaic(frames, mosaic_image_path)
                else:
                    print(f"No frames extracted for video: {video_path}")


# Example usage with relative paths
source_dir = resolve_path('../data/split_data')
output_dir = resolve_path('../data/training_data')
process_videos(source_dir, output_dir)
