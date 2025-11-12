from pathlib import Path
import cv2
import numpy as np
import imagehash
from PIL import Image
import config

from app_code.core.blank_checker import is_blank_img
from app_code.core.rotate_correction import correct_skew


class ImageProcessor:

    @staticmethod
    def get_image_paths(folder_path):

        folder_path = Path(folder_path)

        # 이미지를 찾을 폴더의 경로가 유효한지 확압니다.
        if not folder_path.exists():
            print("경로를 찾을 수 없습니다.")
            return None

        IMAGE_EXTENSIONS = config.IMAGE_EXTENSIONS

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
    def _process_single_image(image_path, folder_path, crop_rect):
        try:

            image_path = Path(image_path)
            img = ImageProcessor.get_safe_load_img(image_path)  # 실제 이미지 로드

            pre_img = correct_skew(img) # 이미지 정렬

            # 자를 이미지의 왼쪽 위, 오른쪽 위, 왼쪽 아래, 오른쪽 아래의 좌표로 이미지를 자릅니다.

            x1, y1, x2, y2 = crop_rect

            cropped = pre_img[y1:y2, x1:x2]
            is_blank = is_blank_img(cropped)  # 백지인지 판단

            pil_img = ImageProcessor.get_process_pli(cropped)  # pil_img로 변경
            image_hash = ImageProcessor.get_image_hash(pil_img)  # 이미지 해시값

            output_path = str(Path(folder_path) / image_path.name)  # 저장 경로 지정            

            # 최종 결과를 반환
            return {
                "pil_data": {
                    "pil_img": pil_img.convert("L"),
                    "output_path": output_path
                },
                "image_data": {
                    "input_path": str(image_path),
                    "pre_path": output_path,
                    "image_hash": str(image_hash),
                    "is_blank": is_blank
                }
            }

        except Exception as e:
            return {
                "input_path": image_path,
                "error": str(e)
            }
