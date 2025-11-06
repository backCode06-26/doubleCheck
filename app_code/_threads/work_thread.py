from pathlib import Path
import cv2
import time
import config
from PySide6.QtCore import QObject, Signal, QRunnable
from app_code.process.image_processor import ImageProcessor
from app_code.core.data_processor import read_json
from skimage.metrics import structural_similarity as ssim

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")


class ImageProcessSignals(QObject):
    double_images = Signal(list)
    blank_images = Signal(list)

    max_progress = Signal(int)
    update_progress = Signal(int)

    progress = Signal(str)
    finished = Signal()


G_LOAD_IMAGES = None
G_SHARE_LIST = None


def compare_single_pair(i, j):
    global G_LOAD_IMAGES
    global G_SHARE_LIST

    first_load_image = G_LOAD_IMAGES[i]
    second_load_image = G_LOAD_IMAGES[j]

    if (first_load_image.shape[2] == 3):
        first_gray_image = cv2.cvtColor(
            first_load_image, cv2.COLOR_BGR2GRAY)
    else:
        first_gray_image = first_load_image

    if (second_load_image.shape[2] == 3):
        second_gray_image = cv2.cvtColor(
            second_load_image, cv2.COLOR_BGR2GRAY)
    else:
        second_gray_image - second_load_image

    w = min(first_gray_image.shape[1], second_gray_image.shape[1])
    h = min(first_gray_image.shape[0], second_gray_image.shape[0])
    first_gray_image = first_gray_image[0:h, 0:w]
    second_gray_image = second_gray_image[0:h, 0:w]

    score = ssim(first_gray_image, second_gray_image, full=False)

    first_input_path = G_SHARE_LIST[j]["input_path"]
    second_input_path = G_SHARE_LIST[i]["input_path"]

    if score >= 0.75:
        result = (first_input_path, second_input_path)
        message = f"중복답안: \"{first_input_path}\", \"{second_input_path}\" (SSIM: {score:.2f})"
        return result, message
    else:
        message = f"중복 아님: \"{first_input_path}\", \"{second_input_path}\" (SSIM: {score:.2f})"
        return None, message


class ImageProcessRunnable(QRunnable):

    def __init__(self):
        super().__init__()
        self.signals = ImageProcessSignals()

    def run(self):

        self.signals.progress.emit("검사시작")

        start_time = time.time()

        share_list = read_json(config.current_json, "data")

        global G_SHARE_LIST
        G_SHARE_LIST = share_list

        load_image_list = [ImageProcessor.get_safe_load_img(
            share["input_path"]) for share in share_list]

        global G_LOAD_IMAGES
        G_LOAD_IMAGES = load_image_list

        blank_image_set = set()
        total = len(share_list)

        tasks = []

        for i in range(total):

            first_data = share_list[i]

            is_blank_i = first_data["is_blank"]
            input_path_i = first_data["input_path"]

            if is_blank_i:
                if input_path_i not in blank_image_set:
                    blank_image_set.add(input_path_i)
                continue

            for j in range(i+1, total):

                second_data = share_list[j]

                is_blank_j = second_data["is_blank"]
                input_path_j = second_data["input_path"]

                if is_blank_j:
                    if input_path_j not in blank_image_set:
                        blank_image_set.add(input_path_j)
                    continue

                first_hash = ImageProcessor.text_to_hash(
                    first_data["image_hash"])
                second_hash = ImageProcessor.text_to_hash(
                    second_data["image_hash"])

                hamming_distance = first_hash - second_hash

                if hamming_distance > config.hash_value:
                    continue

                tasks.append((i, j))

        task_count = len(tasks)
        self.signals.progress.emit(f"총 {task_count}개의 작업이 준비되었습니다.")
        self.signals.max_progress.emit(task_count)

        # 2. Pool 초기화 시 load_image_list를 전달 (Initializer 사용)
        double_image_set = set()

        for idx, task in enumerate(tasks, 1):
            i, j = task
            result, messge = compare_single_pair(i, j)

            self.signals.update_progress.emit(1)
            self.signals.progress.emit(messge)

            self.signals.progress.emit(f"{idx}/{task_count} 데이터를 처리 하고 있습니다.")
            if result:
                img1, img2 = result
                double_image_set.add(img1)
                double_image_set.add(img2)

        blank_image_list = list(blank_image_set)
        double_image_list = list(double_image_set)

        self.signals.blank_images.emit(blank_image_list)
        self.signals.double_images.emit(double_image_list)

        end_time = time.time()

        self.signals.progress.emit("이미지 처리를 완료했습니다.")
        self.signals.progress.emit(
            "-------------------------------------------------------")
        self.signals.progress.emit(f"전체 진행 시간: {end_time - start_time}")
        self.signals.progress.emit(
            "-------------------------------------------------------")
        self.signals.finished.emit()
