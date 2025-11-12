import multiprocessing
import time
from pathlib import Path
import config
from PySide6.QtCore import QObject, Signal, QRunnable
from app_code.core.data_processor import precompute_image_features
from app_code.process.image_processor import ImageProcessor
import traceback
import io


class BatchImagePreprocessingSingnals(QObject):
    progress = Signal(str)
    error = Signal(str)
    result = Signal(object)
    finished = Signal()


def process_image_wrapper(image_path, folder_path, crop_rect):
    """자식 프로세스: 이미지 처리 후 바이트와 출력 경로를 반환"""
    result = ImageProcessor._process_single_image(image_path, folder_path, crop_rect)

    data = result["pil_data"]

    pil_img = data["pil_img"]
    output_path = data["output_path"]
    
    # 결과로 (이미지 바이트 리스트, image_data 반환)
    return (pil_img, output_path), result["image_data"]


class BatchImagePreprocessingRunnable(QRunnable):
    def __init__(self, tasks, crop_rect):
        super().__init__()
        self.signals = BatchImagePreprocessingSingnals()
        self.tasks = tasks
        self.crop_rect = crop_rect

    def run(self):
        try:
            self.signals.progress.emit("전체 이미지 전처리를 시작합니다.")
            all_time = 0

            for i, task in enumerate(self.tasks):
                folder_path = task['root']
                json_path = task['json_path']
                image_paths = task['image_paths']

                self.signals.progress.emit(
                    f"\n[Task {i+1}/{len(self.tasks)}] 처리 시작: {json_path.name}")

                start_time = time.time()
                output_data_path = Path(folder_path) / "data"

                # 뒷장 이미지만 필터링
                tasks_for_pool = [
                    (Path(path), output_data_path, self.crop_rect)
                    for path in image_paths
                    if Path(path).stem[-1] == "2"
                ]

                total_images = len(tasks_for_pool)
                self.signals.progress.emit(
                    f"  > 이미지 {total_images}개 병렬 처리 시작 (코어 수: {config.core_count})")

                # Pool에서 결과 반환
                with multiprocessing.Pool(processes=config.core_count) as pool:
                    results = pool.starmap(process_image_wrapper, tasks_for_pool)

                # 메인 프로세스에서 이미지 저장
                saved_count = 0
                processed_datas = []

                for result in results:
                    (pil_img, output_path), image_data = result

                    processed_datas.append(image_data)

                    # 이미지 데이터를 메인 스레드로 보내기
                    # PIL 이미지를 BytesIO로 변환
                    buf = io.BytesIO()
                    pil_img.save(buf, format="JPEG")
                    buf.seek(0)

                    # Signal로 전달할 때는 dict로
                    self.signals.result.emit({
                        "image_bytes": buf.getvalue(),  # 바이트 데이터만 전달
                        "output_path": str(output_path),  # 경로는 문자열로 전달
                    })

                    saved_count += 1
                    self.signals.progress.emit(f"  > {saved_count}/{total_images} 이미지 저장 완료.")

                # json 생성
                precompute_image_features(folder_path, json_path, image_paths, processed_datas)

                end_time = time.time()

                work_time = end_time - start_time
                config.all_time += work_time
                self.signals.progress.emit(f"  > 작업 처리 시간: {work_time:.2f}초.")

        except Exception as e:
            tb = traceback.format_exc()
            self.signals.error.emit(f"일괄 처리 중 예기치 않은 오류 발생: {e}\n\n스택트레이스:\n{tb}")

        finally:
            self.signals.finished.emit()
