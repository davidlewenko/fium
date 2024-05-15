import os
import random
import shutil


def create_dirs(base_path, dir_names):
    for dir_name in dir_names:
        path = os.path.join(base_path, dir_name)
        os.makedirs(path, exist_ok=True)


def resolve_path(relative_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)


def split_data(source_dir, output_dir):
    categories = ['MEFO', 'negativ']

    for category in categories:
        category_path = os.path.join(source_dir, category)

        # Print the category path for debugging
        print(f"Accessing category path: {category_path}")

        all_files = [os.path.join(category_path, f) for f in os.listdir(category_path) if
                     os.path.isfile(os.path.join(category_path, f))]

        # Shuffle the list of files for randomness
        random.shuffle(all_files)

        # Calculate the quarter length
        quarter_length = len(all_files) // 4

        # Split the files into quarters
        quarter = all_files[:quarter_length]
        rest = all_files[quarter_length:]

        # Create directories for the splits
        category_output_dir = os.path.join(output_dir, category)
        create_dirs(category_output_dir, ['initial_split/train', 'initial_split/test', 'remaining'])

        # Copy the initial quarter to the train and test directories
        train_split_ratio = 0.8  # 80% train, 20% test
        train_files = quarter[:int(len(quarter) * train_split_ratio)]
        test_files = quarter[int(len(quarter) * train_split_ratio):]

        for file in train_files:
            shutil.copy(file, os.path.join(category_output_dir, 'initial_split/train'))

        for file in test_files:
            shutil.copy(file, os.path.join(category_output_dir, 'initial_split/test'))

        # Copy the remaining files to the remaining directory
        for file in rest:
            shutil.copy(file, os.path.join(category_output_dir, 'remaining'))


# Example usage with relative paths
source_dir = resolve_path('../data/raw_videos')
output_dir = resolve_path('../data/split_data')
split_data(source_dir, output_dir)
