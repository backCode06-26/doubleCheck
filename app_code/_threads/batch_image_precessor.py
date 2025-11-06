import multiprocessing
import time
from pathlib import Path
import config
from PySide6.QtCore import QObject, Signal, QRunnable
from app_code.core.data_processor import precompute_image_features
from app_code.process.image_processor import ImageProcessor
import traceback


class BatchImagePreprocessingSingnals(QObject):
    progress = Signal(str)
    error = Signal(str)
    result = Signal(list)  # 최종 결과 리스트를 보냄
    finished = Signal()


def process_image_wrapper(path, folder_path, file_name):
    return ImageProcessor._process_single_image(path, folder_path, file_name)


class BatchImagePreprocessingRunnable(QRunnable):
    def __init__(self, tasks):
        super().__init__()
        self.signals = BatchImagePreprocessingSingnals()
        self.tasks = tasks

    def run(self):
        results = []

        try:
            self.signals.progress.emit("전체 이미지 전처리를 시작합니다.")

            all_time = 0
            for i, task in enumerate(self.tasks):
                root_path = task['root']  # 폴더 경로
                json_path = task['json_path']  # json 파일 경로
                image_paths = task['image_paths']  # 전체 이미지 배열

                self.signals.progress.emit(
                    f"\n[Task {i+1}/{len(self.tasks)}] 처리 시작: {json_path.name}")

                start_time = time.time()

                output_data_path = root_path / "data"  # 이미지 저장 폴더

                # 뒷장 이미지만 필터링한 배열
                tasks_for_pool = [
                    (path, output_data_path, Path(path).name)
                    for path in image_paths
                    if Path(path).stem[-1] == "2"
                ]

                total_images = len(tasks_for_pool)
                processed_image_data = []

                # 이미지 병렬 처리
                # (이미지 경로, 전처리 이미지 경로, 이미지 해쉬, 백지 판단여부)
                self.signals.progress.emit(
                    f"  > 이미지 {total_images}개 병렬 처리 시작 (코어 수: {config.core_count})")

                with multiprocessing.Pool(processes=config.core_count) as pool:
                    result_list = pool.starmap_async(
                        process_image_wrapper, tasks_for_pool).get()

                # 처리한 이미지의 로그 작업
                for idx, result in enumerate(result_list, 1):
                    self.signals.progress.emit(
                        f"  > {idx}/{total_images} 이미지 처리 완료.")
                    processed_image_data.append(result)

                # json 파일 생성 및 작성
                precompute_image_features(
                    root_path, json_path, image_paths)

                end_time = time.time()
                work_time = end_time - start_time

                all_time += work_time

                self.signals.progress.emit(f"  > 작업 처리 시간: {work_time:.2f}초.")

            self.signals.progress.emit(f"> 전체 작업 시간: {all_time:.2f}초.")

            self.signals.result.emit(results)

        except Exception as e:
            self.signals.error.emit(f"일괄 처리 중 예기치 않은 오류 발생: {e}")

        finally:
            self.signals.finished.emit()
