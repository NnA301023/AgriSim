import cv2 as cv
import numpy as np
import pandas as pd
from collections import Counter
from typing import Tuple, Union, List


def load_metadata_plant(file: str = "static/metadata.xlsx") -> pd.DataFrame:
    data = pd.read_excel(io = file, sheet_name = "komoditas pasar")
    return data

def read_image(file: str = "static/karawang.png") -> np.array:
    image_original = cv.imread(filename = file)
    image_original = cv.cvtColor(image_original, cv.COLOR_BGR2RGB)
    return image_original

def grid_apply(image: np.array, grid_size: int = 10) -> np.array:
    result = image.copy()
    h, w, _ = image.shape
    for y in range(0, h, grid_size):
        cv.line(result, (0, y), (w, y), (255, 0, 0), 1)
    for x in range(0, w, grid_size):
        cv.line(result, (x, 0), (x, h), (255, 0, 0), 1)
    return result

def segment_green_area(
    image: np.array, grid_image: np.array,
    is_plant: bool = False,
    lower_bound: np.array = np.array([70, 25, 0]),
    upper_bound: np.array = np.array([105, 255, 125])
    ) -> Tuple[np.array, Union[List[int], int]]:

    # Masking green area
    image = image.copy()
    hsv_image = cv.cvtColor(image, cv.COLOR_RGB2HSV)
    masking = cv.inRange(hsv_image, lower_bound, upper_bound)

    # Contour filter detection
    large_area = np.zeros_like(masking)
    _min_area_threshold = []
    contours, _ = cv.findContours(masking, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area_contour = cv.contourArea(contour)
        _min_area_threshold.append(area_contour)
    min_area_threshold = sorted(set(_min_area_threshold))
    min_area_threshold = np.quantile(min_area_threshold, 0.95)
    final_area_capture = []
    for contour in contours:
        area_contour = cv.contourArea(contour)
        if area_contour >= min_area_threshold:
            final_area_capture.append(int(area_contour))
            cv.drawContours(large_area, [contour], 0, 255, thickness = cv.FILLED)
    if is_plant is False:
        final_area_capture = sum(final_area_capture) # pixel based value
    else:
        final_area_capture = list(_min_area_threshold)
      
    # Filter result with median filtering
    large_area = cv.medianBlur(cv.cvtColor(large_area, cv.COLOR_GRAY2RGB), 15)[:,:,0]
    result = cv.bitwise_and(grid_image, grid_image, mask = large_area)
    return result, final_area_capture, large_area


def area_plant_calculation(
    image: np.array, 
    lower_bound: np.array = np.array([70, 25, 0]),
    upper_bound: np.array = np.array([105, 255, 125])
    ) -> Tuple[int, int]:

    # Masking green area
    hsv_image = cv.cvtColor(image, cv.COLOR_RGB2HSV)
    masking = cv.inRange(hsv_image, lower_bound, upper_bound)

    # Contour filter detection
    large_area = np.zeros_like(masking)
    min_area_threshold = []
    contours, _ = cv.findContours(masking, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area_contour = cv.contourArea(contour)
        min_area_threshold.append(area_contour)
    min_area_threshold = sorted(set(min_area_threshold))
    min_area_threshold = max(min_area_threshold)
    final_area_capture = []
    for contour in contours:
        area_contour = cv.contourArea(contour)
        if area_contour >= min_area_threshold:
            final_area_capture.append(int(area_contour))
            cv.drawContours(large_area, [contour], 0, 255, thickness = cv.FILLED) # Contour Detect per Area

    # Square planting calculation
    area_grid_square = list(final_area_capture)
    area_grid_square = dict(Counter(area_grid_square))
    stable_grid_area = max(area_grid_square, key = area_grid_square.get)
    length_grid_area = area_grid_square[stable_grid_area]
    return stable_grid_area, length_grid_area