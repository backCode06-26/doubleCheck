from PySide6.QtCore import QObject, Signal, QRunnable, Slot
import multiprocessing
from code.process.image_processor import ImageProcessor
import config
import time
import os


class ImagePreprocessingSingnals(QObject):
    progress = Signal(str)
    error = Signal(str)
    result = Signal(list)
    finished = Signal()


def process_image_wrapper(path, folder_path, file_name):
    return ImageProcessor._process_single_image(path, folder_path, file_name)


class ImagePreprocessingRunnable(QRunnable):
    def __init__(self, image_paths, max_workers=4):
        super().__init__()
        self.signals = ImagePreprocessingSingnals()
        self.image_paths = image_paths
        self.max_workers = max_workers

    @Slot()
    def run(self):
        try:

            self.signals.progress.emit("이미지 전처리를 시작합니다.")
            start_time = time.time()

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

            end_time = time.time()

            work_time = end_time - start_time
            self.signals.progress.emit("\n전체 이미지 처리를 완료하였습니다.")
            self.signals.progress.emit(f"작업에 걸린 시간: {work_time}")
            config.all_time += work_time
            self.signals.result.emit(results)
            self.signals.finished.emit()

        except Exception as e:
            self.signals.error.emit(str(e))
