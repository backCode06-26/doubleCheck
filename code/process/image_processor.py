import os
import cv2
import numpy as np
import imagehash
from PIL import Image

import config
from code.core.blank_checker import isBlankImage
from code.core.rotate_correction import correct_skew


class ImageProcessor:

    @staticmethod
    def getImagePaths(folder_path):

        # 이미지를 찾을 폴더의 경로가 유효한지 확압니다.
        if not os.path.isdir(folder_path):
            print("경로를 찾을 수 없습니다.")
            return None

        IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")  # 허용되는 확장자

        # 폴더 안 이미지의 경로를 가져옵니다.
        image_paths = [
            # os.path.join(self.existing_path, f).replace("\\", "/")
            ImageProcessor.getClearPath(os.path.join(folder_path, f))
            for f in os.listdir(folder_path)
            if f.lower().endswith(IMAGE_EXTENSIONS)
        ]

        # 이미지가 존재하는지 확인합니다.
        if not image_paths:
            print("선택한 폴더에 이미지가 없습니다.")
            return None

        return image_paths

    def getClearPath(path):
        return path.replace("\\", "/")

    @staticmethod
    def getSafeImgLoad(img_path):
        with open(img_path, "rb") as f:
            file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        return img

    @staticmethod
    def getProcessedPil(cv_img):
        cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cv_img_rgb)

    @staticmethod
    def getImageHash(pil_img):
        hash_value = imagehash.phash(pil_img)
        return hash_value

    def textToHash(text):
        return imagehash.hex_to_hash(text)

    @staticmethod
    def saveImage(pil_img, output_path):
        img_gray = pil_img.convert('L')
        img_gray.save(output_path)

    @staticmethod
    def _process_single_image(path, folder_path, file_name):
        try:
            img = ImageProcessor.getSafeImgLoad(path)
            pre_img = correct_skew(img)
            is_blank = isBlankImage(pre_img)
            pil_img = ImageProcessor.getProcessedPil(pre_img)

            output_path = os.path.join(
                folder_path, file_name).replace("\\", "/")

            image_hash = ImageProcessor.getImageHash(pil_img)

            ImageProcessor.saveImage(pil_img, output_path)

            # 최종 결과를 반환
            return {
                "input_path": path,
                "pre_path": output_path,
                "image_hash": str(image_hash),
                "is_blank": is_blank
            }

        except Exception as e:
            return {
                "input_path": path,
                "error": str(e)
            }
