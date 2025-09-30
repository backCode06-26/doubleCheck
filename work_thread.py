
import os
import cv2
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

    def __init__(self, folder_path, batch_size=5):
        super().__init__()
        self.signals = ImageProcessSignals()

        self.folder_path = folder_path
        self.batch_size = batch_size

    def run(self):

        self.blank_paths = []
        self.double_paths = []

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

                if image_files[i] in self.blank_paths:
                    continue

                share_list.pop(main_idx)

                self.signals.progress.emit(f"{image_files[i]}: 백지답안")
                self.blank_paths.append(image_files[i])

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

                    if image_files[j] in self.blank_paths:
                        continue

                    share_list.pop(sub_idx)

                    self.signals.progress.emit(f"{image_files[j]}: 백지답안")
                    self.blank_paths.append(image_files[j])

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

                score = ssim(first_img, second_img, full=False)
                print(score)

                if score >= 0.75:
                    self.double_paths.append(image_files[i])
                    self.double_paths.append(image_files[j])

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
