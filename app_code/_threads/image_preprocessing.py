from PySide6.QtCore import QObject, Signal, QRunnable, Slot
import multiprocessing
from app_code.process.image_processor import ImageProcessor
import config
import time
import os


class ImagePreprocessingSingnals(QObject):
    progress = Signal(str)
    error = Signal(str)
    result = Signal(list)
    finished = Signal()


class ImagePreprocessingRunnable(QRunnable):
    def __init__(self, image_paths):
        super().__init__()
        self.signals = ImagePreprocessingSingnals()
        self.image_paths = image_paths

    @Slot()
    def run(self):
        try:

            self.signals.progress.emit("이미지 전처리를 시작합니다.")
            start_time = time.time()  # 시작 시간

            self.signals.progress.emit(f"사용한 코어 수: {config.core_count}\n")

            results = []

            output_path = os.path.join(
                os.path.dirname(self.image_paths[0]), "data")

            tasks = [(path, output_path, os.path.basename(path))
                     for path in self.image_paths]
            total = len(tasks)

            with multiprocessing.Pool(processes=config.core_count) as pool:
                result_list = pool.starmap_async(
                    process_image_wrapper, tasks).get()

            for idx, result in enumerate(result_list, 1):
                self.signals.progress.emit(f"{idx}/{total} 작업이 완료되었습니다.")
                results.append(result)

            end_time = time.time()  # 끝난 시간

            work_time = end_time - start_time  # 전체 계산 시간

            self.signals.progress.emit("\n전체 이미지 처리를 완료하였습니다.")
            self.signals.progress.emit(f"작업에 걸린 시간: {work_time}")

            config.all_time += work_time  # 전체 시간에 합산
            self.signals.result.emit(results)  # 계산한 데이터 전달
            self.signals.finished.emit()

        except Exception as e:
            self.signals.error.emit(str(e))
