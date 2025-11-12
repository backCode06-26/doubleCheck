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

    def __init__(self, json_path):
        super().__init__()
        self.signals = ImageProcessSignals()
        self.json_path = json_path

    def run(self):

        self.signals.progress.emit("전체 이미지 검사를 시작합니다.")

        # 시작 시간 측정
        start_time = time.time()

        # 전처리된 데이터
        share_list = read_json(self.json_path, "data")

        # 로드된 이미지
        load_image_list = [ImageProcessor.get_safe_load_img(
            share["input_path"]) for share in share_list]

        # 전역 함수로 외부로 데이터를 전달합니다.
        # 함수에 매개변수로 받으면 데이터를 복사해야해서 속도가 느려짐

        # 전처리된 데이터
        global G_SHARE_LIST
        G_SHARE_LIST = share_list

        # 로드된 이미지
        global G_LOAD_IMAGES
        G_LOAD_IMAGES = load_image_list

        total = len(share_list) # 전체 데이터 개수


        blank_image_set = set() # 백지 이미지
        tasks = [] # 검사 데이터 배열

        for i in range(total):

            # 첫번째 데이터
            first_data = share_list[i]

            is_blank_i = first_data["is_blank"] # 백지인지 아닌지
            input_path_i = first_data["input_path"] # 전처리 전 이미지 경로

            # 백지인지
            if is_blank_i:
                # 백지로 구분이 된 이미지 인지
                if input_path_i not in blank_image_set:
                    blank_image_set.add(input_path_i)
                continue

            for j in range(i+1, total):

                # 두번째 데이터
                second_data = share_list[j]

                is_blank_j = second_data["is_blank"] # 백지인지 아닌지
                input_path_j = second_data["input_path"] # 전처리 전 이미지 경로

                # 백지 인지
                if is_blank_j:
                    # 백지로 구분이 된 이미지 인지
                    if input_path_j not in blank_image_set:
                        blank_image_set.add(input_path_j)
                    continue

                first_hash = ImageProcessor.text_to_hash(
                    first_data["image_hash"]) # 첫번째 이미지 해쉬
                second_hash = ImageProcessor.text_to_hash(
                    second_data["image_hash"]) # 두번째 이미지 해쉬

                # 이미지 해쉬의 해밍거리 계산
                hamming_distance = first_hash - second_hash

                # 계산된 해밍거리와 허용된 임계값을 비교
                # 해밍거리 보다 임계값이 커지면 서로 다르다고 판단
                # 유사도 검사를 건너뜹니다.
                if hamming_distance > config.hash_value:
                    continue

                # 유사도 검사을 진행할 데이터만 저장
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
        
        work_time = end_time - start_time
        config.all_time += work_time

        self.signals.progress.emit("이미지 처리를 완료했습니다.")
        self.signals.progress.emit(
            "-------------------------------------------------------")
        self.signals.progress.emit(f"  > 작업 처리 시간: {work_time:.2f}초.")
        self.signals.progress.emit(
            "-------------------------------------------------------")
        self.signals.finished.emit()
