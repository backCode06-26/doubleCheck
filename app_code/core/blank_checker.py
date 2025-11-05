import cv2
import numpy as np
from app_code.core.extract_region import crop_roi

# import os

# folder_path = "C:/Users/hojin/OneDrive/Desktop/이중급지 테스트용 답안"

# IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")
# image_paths = [
#     os.path.join(folder_path, f)
#     for f in os.listdir(folder_path)
#     if f.lower().endswith(IMAGE_EXTENSIONS)
# ]


def is_blank_img(img):

    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)

    white_ratio = np.sum(thresh == 255) / thresh.size

    if white_ratio >= 0.976:
        return True
    else:
        return False
