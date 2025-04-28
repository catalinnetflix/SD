import time
from pathlib import Path
import cv2
import numpy as np

EXTENSION_WEIGHTS = {
    ".md": 8, ".txt": 7, ".json": 5, ".csv": 5, ".log": 2,".bmp":7
}

DIR_PRIORITY = {
    "docs": 10,
    "important": 8,
    "projects": 6,
    "tmp": -2,
    "trash": -5,
}

COLOR_RANGES = {
    "red": ([0, 50, 50], [10, 255, 255]),
    "green": ([35, 50, 50], [85, 255, 255]),
    "blue": ([100, 50, 50], [130, 255, 255]),
    "orange": ([5, 150, 150], [15, 255, 255]),
    "yellow": ([25, 150, 150], [35, 255, 255]),
    "purple": ([140, 50, 50], [160, 255, 255])
}

def calculate_color_dominance(image, target_color):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_bound = np.array(COLOR_RANGES[target_color][0])
    upper_bound = np.array(COLOR_RANGES[target_color][1])

    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)

    color_pixels = np.sum(mask) / 255
    total_pixels = image.size / 3

    color_prominence = color_pixels / total_pixels
    return color_prominence


def compute_score(filepath: str, content: str, extension: str, size: int, timestamp: float,
                  query_terms: list[str] = []):
    score = 0

    if not isinstance(filepath, str):
        raise ValueError(f"Expected a string for filepath, but got {type(filepath)}")

    path = Path(filepath).as_posix().lower()

    if isinstance(timestamp, str):
        try:
            timestamp = float(timestamp)
        except ValueError:
            timestamp = time.time()

    if any(term.lower() in path for term in query_terms):
        score += 10

    score += EXTENSION_WEIGHTS.get(extension, 1)

    if 500 < size < 500_000:
        score += 5
    elif size > 1_000_000:
        score -= 3

    if timestamp:
        age = time.time() - timestamp
        if age < 86400:
            score += 10
        elif age < 604800:
            score += 5
        elif age < 2592000:
            score += 2

    if len(query_terms) >= 2:
        score += 7

    for folder in DIR_PRIORITY:
        if f"/{folder}/" in path or path.endswith(f"/{folder}"):
            score += DIR_PRIORITY[folder]
            break

    if extension.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
        image = cv2.imread(filepath)

        if image is None:
            raise ValueError(f"Could not read image at {filepath}")

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        target_colors = ["red", "green", "blue", "orange", "yellow", "purple"]

        color_scores = {}
        for color in target_colors:
            color_scores[color] = calculate_color_dominance(image, color)
        max_color = max(color_scores, key=color_scores.get)
        color_dominance = color_scores[max_color]

        score += color_dominance * 20

    return int(score)

