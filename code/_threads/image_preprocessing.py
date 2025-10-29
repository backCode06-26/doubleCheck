from PySide6.QtCore import QObject, Signal, QRunnable, Slot
from concurrent.futures import ThreadPoolExecutor
from code.process.image_processor import ImageProcessor
import config
import time


class ImagePreprocessingSingnals(QObject):
    progress = Signal(str)
    error = Signal(str)
    result = Signal(list)
    finished = Signal()


def process_image_wrapper(path):
    """pickle 가능한 전역 함수"""
    return ImageProcessor._process_single_image(path)


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

            results = []
            total = len(self.image_paths)

            # 멀티프로세싱으로 병렬 처리
            with ThreadPoolExecutor(max_workers=config.core_count) as executor:
                # 모든 작업을 한 번에 제출
                futures = {
                    executor.submit(process_image_wrapper, path): path
                    for path in self.image_paths
                }

                # 완료된 작업부터 순차적으로 수집
                start_time = time.time()

                from concurrent.futures import as_completed
                for idx, future in enumerate(as_completed(futures), 1):
                    try:
                        image_data = future.result()
                        results.append(image_data)
                        self.signals.progress.emit(f"{idx}/{total} 이미지 전처리 완료")
                    except Exception as e:
                        self.signals.error.emit(f"이미지 처리 오류: {str(e)}")

                end_time = time.time()

                work_time = end_time - start_time

            self.signals.progress.emit("전체 이미지 처리를 완료하였습니다.")
            self.signals.progress.emit(f"작업에 걸린 시간: {work_time}")
            config.all_time += work_time
            self.signals.result.emit(results)
            self.signals.finished.emit()

        except Exception as e:
            self.signals.error.emit(str(e))
