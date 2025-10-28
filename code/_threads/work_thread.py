import os
import cv2
import time
from PySide6.QtCore import QObject, Signal, QRunnable
from skimage.metrics import structural_similarity as ssim

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

        self.main_start = time.time()

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
            self.file_start = time.time()

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

                # 이미지 정확도 계산
                hamming_distance = hash1 - hash2
                print("계산된 hash값: ", hamming_distance)
                print("기준 hash값: ", self.hash_value)

                # 이 해시값 GUI에서 받아야함
                if hamming_distance <= self.hash_value:

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

            self.file_end = time.time()
            self.signals.progress.emit(
                f"\n\n파일 처리 시간 {self.file_end - self.file_start:4f}초\n\n")

        self.main_end = time.time()

        self.signals.blank_images.emit(self.blank_paths)
        self.signals.double_images.emit(self.double_paths)
        self.signals.finished.emit()
        self.signals.progress.emit("검사완료")
        self.signals.progress.emit(
            f"\n\n전체 처리 시간 {self.main_end - self.main_start:4f}초")
