
import os
import cv2
import numpy as np
from blank_checker import is_blank_page
from PySide6.QtCore import QObject, Signal, QRunnable
from skimage.metrics import structural_similarity as ssim

from rotate_correction import correct_skew

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")


class ImageProcessSignals(QObject):
    double_images = Signal(list)
    blank_images = Signal(list)

    max_main_progress = Signal(int)
    update_main_progress = Signal(int)

    progress = Signal(str)
    finished = Signal()


class ImageProcessRunnable(QRunnable):

    def __init__(self, folder_path, hash_value, batch_size=5):
        super().__init__()
        self.signals = ImageProcessSignals()

        self.folder_path = folder_path
        self.hash_value = hash_value
        self.batch_size = batch_size

    def run(self):

        def phash_cv(img):

            # 2. 크기 조정
            img = cv2.resize(img, (32, 32))

            # 3. DCT 적용(저주파(큰 구조), 고주파(세부 구조))
            dct = cv2.dct(np.float32(img))

            # 4. 상위 8x8 영역 추출 (저주파 추출)
            dct_roi = dct[:8, :8]

            # 5. 평균값 기준으로 0/1 결정
            avg = dct_roi.mean() # 저주파의 평균값 구하기

            # 저주파 영역에서 평균값보다 크면 True 작으면 False로 재구성합니다.
            hash_array = dct_roi > avg

            # 6. 64비트 해시 생성 (재구성된 배열을 1과 0으로 다시 재구성합니다.)
            hash_str = ''.join(['1' if x else '0' for x in hash_array.flatten()])
            hash = int(hash_str, 2)
            return hash

        def compare_image(hash1, hash2):
            diff = bin(hash1 ^ hash2).count("1")
            similarity = 1 - (diff / 64)
            return similarity

        self.blank_paths = []
        self.blank_sceen = set()

        self.double_paths = []
        self.double_sceen = set()

        self.signals.progress.emit("검사시작")

        if not self.folder_path:
            self.signals.progress.emit("폴더 경로 없음")
            self.signals.finished.emit()
            return

        # 이미지 파일 리스트
        image_files = [
            f for f in os.listdir(self.folder_path)
            if f.lower().endswith(IMAGE_EXTENSIONS)
        ]

        # 이미지의 전체 개수
        total = len(image_files)

        share_list = list(range(1, total, 2))

        # 비교 이미지
        main_idx = 0
        while main_idx < len(share_list):
            i = share_list[main_idx]

            # 비교할 이미지의 최대값
            self.signals.max_main_progress.emit(len(list(range(1, total, 2))))

            first_path = os.path.join(
                self.folder_path, image_files[i]).replace("\\", "/")

            # 첫 이미지 백지 체크
            if is_blank_page(first_path):

                if image_files[i] in self.blank_sceen:
                    continue

                share_list.pop(main_idx)

                self.signals.progress.emit(f"{image_files[i]}: 백지답안")
                self.blank_paths.append(image_files[i])
                self.blank_sceen.add(image_files[i])

                # 비교 진행도 초기화
                self.signals.update_main_progress.emit(1)
                continue

            # 대조 이미지
            sub_idx = main_idx+1
            while sub_idx < len(share_list):
                j = share_list[sub_idx]

                second_path = os.path.join(
                    self.folder_path, image_files[j]).replace("\\", "/")

                if is_blank_page(second_path):

                    if image_files[j] in self.blank_sceen:
                        continue

                    share_list.pop(sub_idx)

                    self.signals.progress.emit(f"{image_files[j]}: 백지답안")
                    self.blank_paths.append(image_files[j])
                    self.blank_sceen.add(image_files[j])

                    continue

                try:
                    origin_first_img = correct_skew(first_path)
                    first_img = cv2.cvtColor(
                        origin_first_img, cv2.COLOR_RGB2GRAY)

                    origin_second_img = correct_skew(second_path)
                    second_img = cv2.cvtColor(
                        origin_second_img, cv2.COLOR_RGB2GRAY)

                except Exception as e:
                    self.signals.progress.emit(f"처리 중 오류 {e}")
                    continue

                if first_img is None or second_img is None:
                    self.signals.progress.emit(
                        f"{image_files[i]} 또는 {image_files[j]} 이미지 없음")

                    continue

                w = min(first_img.shape[1], second_img.shape[1])
                h = min(first_img.shape[0], second_img.shape[0])

                first_img = first_img[0:h, 0:w]
                second_img = second_img[0:h, 0:w]
                
                # 이미지 해쉬 변환
                first_hash = phash_cv(first_img)
                second_hash = phash_cv(second_img)

                # 이미지 정확도 계산
                hamming_distance = compare_image(first_hash, second_hash)

                # 이 해시값 GUI에서 받아야함
                if hamming_distance >= self.hash_value:

                    score = ssim(first_img, second_img, full=False)
                    print(score)

                    if score >= 0.75:
                        if image_files[i] not in self.double_sceen:
                            self.double_paths.append(image_files[i])
                            self.double_sceen.add(image_files[i])

                        if image_files[j] not in self.double_sceen:
                            self.double_paths.append(image_files[j])
                            self.double_sceen.add(image_files[j])

                        self.signals.progress.emit(
                            f"{image_files[i]}, {image_files[j]}: 중복답안")
                    else:
                        self.signals.progress.emit(
                            f"{image_files[i]}, {image_files[j]}: 중복 아님")

                sub_idx += 1
            main_idx += 1

            # 비교 진행도 추가
            self.signals.update_main_progress.emit(1)

        self.signals.blank_images.emit(self.blank_paths)
        self.signals.double_images.emit(self.double_paths)
        self.signals.finished.emit()
        self.signals.progress.emit("검사완료")
