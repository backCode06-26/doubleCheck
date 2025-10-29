import os
import cv2
import time
import config
from PySide6.QtCore import QObject, Signal, QRunnable
from code.process.image_processor import ImageProcessor
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

        self.signals.progress.emit("검사시작")

        if not self.folder_path:
            self.signals.progress.emit("폴더 경로 없음")
            self.signals.finished.emit()
            return

        share_list = config.current_json["data"]
        total = len(share_list)
        blank_image_set = set()
        double_image_set = set()

        blank_image_list = []
        double_image_list = []

        # 비교 이미지
        for i in range(total):
            self.file_start = time.time()

            first_data = share_list[i]
            first_input_path, first_image_hash, first_is_blank, first_pre_path = (
                first_data["input_path"],
                ImageProcessor.textToHash(first_data["image_hash"]),
                first_data["is_blank"],
                first_data["pre_path"]
            )

            # 첫 이미지 백지 체크
            if first_is_blank or (first_input_path in blank_image_set):

                if not (first_input_path in blank_image_set):
                    blank_image_set.add(first_input_path)
                    blank_image_list.append(first_input_path)
                    self.signals.progress.emit(f"{first_input_path}: 백지답안")
                continue

            # 대조 이미지
            for j in range(i+1, total):
                second_data = share_list[j]
                second_input_path, second_image_hash, second_is_blank, second_pre_path = (
                    second_data["input_path"],
                    ImageProcessor.textToHash(second_data["image_hash"]),
                    second_data["is_blank"],
                    second_data["pre_path"]
                )

                if second_is_blank or (second_input_path in blank_image_set):

                    if not (second_input_path in blank_image_set):
                        blank_image_set.add(second_input_path)
                        blank_image_list.append(second_input_path)
                        self.signals.progress.emit(
                            f"{second_input_path}: 백지답안")
                    continue

                try:
                    first_img = ImageProcessor.getSafeImgLoad(
                        first_pre_path)
                    second_img = ImageProcessor.getSafeImgLoad(
                        second_pre_path)

                except Exception as e:
                    self.signals.progress.emit(f"처리 중 오류 {e}")
                    continue

                if first_img is None or second_img is None:
                    self.signals.progress.emit(
                        f"{first_input_path} 또는 {second_input_path} 이미지 없음")

                    continue

                w = min(first_img.shape[1], second_img.shape[1])
                h = min(first_img.shape[0], second_img.shape[0])

                first_img = first_img[0:h, 0:w]
                second_img = second_img[0:h, 0:w]

                # 이미지 정확도 계산
                hamming_distance = first_image_hash - second_image_hash
                print("계산된 hash값: ", hamming_distance)
                print("기준 hash값: ", self.hash_value)

                # 이 해시값 GUI에서 받아야함
                if hamming_distance <= self.hash_value:

                    score = ssim(first_img, second_img, full=False,
                                 win_size=3, gaussian_weights=True)
                    print(score)

                    if score >= 0.75:
                        if first_input_path not in double_image_set:
                            double_image_list.append(first_input_path)
                            double_image_set.add(first_input_path)

                        if second_input_path not in double_image_set:
                            double_image_list.append(second_input_path)
                            double_image_set.add(second_input_path)

                        self.signals.progress.emit(
                            f"{first_input_path}, {second_input_path}: 중복답안")
                    else:
                        self.signals.progress.emit(
                            f"{first_input_path}, {second_input_path}: 중복 아님")

            # 비교 진행도 추가
            self.signals.update_main_progress.emit(1)

            self.file_end = time.time()
            self.signals.progress.emit(
                f"\n\n파일 처리 시간 {self.file_end - self.file_start}\n\n")

        self.main_end = time.time()

        self.signals.blank_images.emit(blank_image_list)
        self.signals.double_images.emit(double_image_list)
        self.signals.finished.emit()
        self.signals.progress.emit("검사완료")
        self.signals.progress.emit(
            f"\n\n전체 처리 시간 {self.main_end - self.main_start}")
