import os
import random
import string
import json
from pathlib import Path

TEXT_EXTENSIONS = {".txt", ".md", ".log", ".csv", ".json"}

NUM_DIRECTORIES = 100
MAX_NESTING_LEVEL = 5
FILES_PER_DIRECTORY = 3

BASE_DIR = "generated_dataset2"

def generate_random_content(file_extension):
    # Define file size category (in bytes)
    size_category = random.choices(
        ["small", "medium", "large"],
        weights=[0.5, 0.3, 0.2],
        k=1
    )[0]

    if size_category == "small":
        length = random.randint(100, 1000)
    elif size_category == "medium":
        length = random.randint(1000, 5000)
    else:
        length = random.randint(5000, 20000)

    if file_extension == ".json":
        return json.dumps({
            "data": [random.randint(1, 100) for _ in range(length // 5)],
            "meta": ''.join(random.choices(string.ascii_letters + string.digits, k=length // 5))
        }, indent=2)
    else:
        return ''.join(random.choices(
            string.ascii_letters + string.digits + string.punctuation + " \n",
            k=length
        ))

def create_files_in_directory(current_path, current_depth):
    if current_depth >= MAX_NESTING_LEVEL:
        return

    for _ in range(FILES_PER_DIRECTORY):
        file_extension = random.choice(list(TEXT_EXTENSIONS))
        filename = ''.join(random.choices(string.ascii_letters, k=10)) + file_extension
        file_path = current_path / filename

        with open(file_path, 'w', encoding='utf-8') as file:
            file_content = generate_random_content(file_extension)
            file.write(file_content)

    for _ in range(random.randint(1, 3)):
        subdir_name = ''.join(random.choices(string.ascii_letters, k=8))
        subdir_path = current_path / subdir_name
        subdir_path.mkdir(exist_ok=True)
        create_files_in_directory(subdir_path, current_depth + 1)

def generate_dataset():
    base_path = Path(BASE_DIR)
    base_path.mkdir(exist_ok=True)

    for _ in range(NUM_DIRECTORIES):
        subdir_name = ''.join(random.choices(string.ascii_letters, k=8))
        subdir_path = base_path / subdir_name
        subdir_path.mkdir(exist_ok=True)
        create_files_in_directory(subdir_path, 0)

    print(f"Dataset with {NUM_DIRECTORIES} directories and varied file sizes generated under {BASE_DIR}.")

if __name__ == "__main__":
    generate_dataset()
