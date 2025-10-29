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
    def getSafeImgLoad(img_path):
        with open(img_path, "rb") as f:
            file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        return img

    @staticmethod
    def cv2ToPIL(img):
        cv_img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(cv_img_rgb)
        return pil_img

    @staticmethod
    def getImageHash(img):
        pil_img = ImageProcessor.cv2ToPIL(img)
        hash_value = imagehash.phash(pil_img)
        return hash_value

    def textToHash(text):
        return imagehash.hex_to_hash(text)

    @staticmethod
    def saveImage(img, output_path):
        pil_img = ImageProcessor.cv2ToPIL(img)
        img_gray = pil_img.convert('L')
        img_gray.save(output_path)

    @staticmethod
    def _process_single_image(path):
        try:
            img = ImageProcessor.getSafeImgLoad(path)

            file_name = os.path.basename(path)
            # config 모듈이 모든 프로세스에서 로드 가능해야 함
            output_folder_path = config.OUTPUT_FOLDER_PATH

            pre_img = correct_skew(img)  # 외부 함수 호출

            output_path = os.path.join(
                output_folder_path, file_name).replace("\\", "/")
            ImageProcessor.saveImage(pre_img, output_path)

            image_hash = ImageProcessor.getImageHash(pre_img)
            is_blank = isBlankImage(pre_img)  # 외부 함수 호출

            # 최종 결과를 반환
            return {
                "input_path": path,
                "pre_path": output_path,
                "image_hash": str(image_hash),
                "is_blank": is_blank
            }

        except Exception as e:
            return {
                "error": str(e)
            }


# def batch_process_images(image_paths):
#     try:
#         total = len(image_paths)
#         print(f"전체 이미지: {total}")

#         with Pool(config.core_count) as pool:
#             results = []

#             for i, result in enumerate(pool.imap(ImageProcessor._process_single_image, image_paths), 1):
#                 results.append(result)
#                 print(
#                     f"[PROGRESS] {i}/{total}: {os.path.basename(image_paths[i-1])}")

#         with open(config.JSON_PATH, 'w', encoding='utf-8') as f:
#             json.dump(results, f, indent=4, ensure_ascii=False)

#         print(f"[STATUS] 완료: 이미지 전처리 결과를 '{config.JSON_PATH}'에 저장하였습니다.")

#     except Exception as e:
#         print(f"[ERROR] 배치 처리 중 치명적인 에러 발생: {e}")
#         # 오류가 발생하면 종료 코드 1로 프로그램 종료
#         exit(1)


# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(
#         description='멀티프로세스를 사용하여 이미지 배치 전처리를 수행합니다.'
#     )

#     parser.add_argument(
#         '--image_paths',
#         nargs="+",
#         required=True,
#         help='처리할 이미지의 경로을 입력해주세요'
#     )

#     args = parser.parse_args()

#     # 메인 함수 실행
#     batch_process_images(args.image_paths)
