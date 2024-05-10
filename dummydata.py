import os
import random
import string
import zipfile
import argparse
from tqdm import tqdm

def generate_dummy_data(size, progress_bar):
    """Generate random dummy data of specified size."""
    data = ''.join(random.choices(string.ascii_letters + string.digits, k=size))
    for _ in tqdm(range(size), desc='Generating Data', disable=not progress_bar):
        pass
    return data

def create_zip_file(filename, size, progress_bar):
    """Create a zip file filled with dummy data."""
    with zipfile.ZipFile(filename, 'w') as zipf:
        # Create a dummy file of the desired size
        dummy_data = generate_dummy_data(size * 1024 * 1024, progress_bar)  # Convert MB to bytes
        with tqdm(total=1, desc='Creating ZIP File', disable=not progress_bar) as pbar:
            zipf.writestr('dummy_data.txt', dummy_data)
            pbar.update(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a dummy data zip file.")
    parser.add_argument("size", type=int, help="Desired size of the dummy data in megabytes")
    parser.add_argument("--no-progress-bar", action="store_true", help="Disable progress bars")

    args = parser.parse_args()
    desired_size_mb = args.size
    show_progress_bar = not args.no_progress_bar

    zip_file_name = f"dummy_data_{desired_size_mb}mb.zip"

    create_zip_file(zip_file_name, desired_size_mb, show_progress_bar)
    print(f"Dummy data zip file '{zip_file_name}' created with size {desired_size_mb} MB.")

