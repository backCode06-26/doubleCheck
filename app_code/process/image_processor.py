from pathlib import Path
import cv2
import numpy as np
import imagehash
from PIL import Image

from app_code.core.blank_checker import is_blank_img
from app_code.core.rotate_correction import correct_skew


class ImageProcessor:

    @staticmethod
    def get_image_paths(folder_path):

        # 이미지를 찾을 폴더의 경로가 유효한지 확압니다.
        if not folder_path.exists():
            print("경로를 찾을 수 없습니다.")
            return None

        IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")  # 허용되는 확장자

        # 폴더 안 이미지의 경로를 가져옵니다.
        image_paths = [
            f.as_posix()
            for f in folder_path.glob('*')
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
        ]

        # 이미지가 존재하는지 확인합니다.
        if not image_paths:
            print("선택한 폴더에 이미지가 없습니다.")
            return None

        return image_paths

    @staticmethod
    def get_safe_load_img(img_path):
        with open(img_path, "rb") as f:
            file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        return img

    @staticmethod
    def get_process_pli(cv_img):
        cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cv_img_rgb)

    @staticmethod
    def get_image_hash(pil_img):
        hash_value = imagehash.phash(pil_img)
        return hash_value

    def text_to_hash(text):
        return imagehash.hex_to_hash(text)

    @staticmethod
    def save_image(pil_img, output_path):
        img_gray = pil_img.convert('L')
        img_gray.save(output_path)

    @staticmethod
    def _process_single_image(path, folder_path, file_name):
        try:
            img = ImageProcessor.get_safe_load_img(path)  # 실제 이미지 로드

            pre_img = correct_skew(img)
            pil_img = ImageProcessor.get_process_pli(pre_img)  # pil_img로 변경

            is_blank = is_blank_img(pre_img)  # 백지인지 판단
            image_hash = ImageProcessor.get_image_hash(pil_img)  # 이미지 해시값

            output_path = str(folder_path / file_name)  # 저장 경로 지정

            ImageProcessor.save_image(pil_img, output_path)

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
