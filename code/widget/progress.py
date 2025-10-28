from PySide6.QtWidgets import (
    QWidget, QProgressBar
)

class Progress(QWidget):
    def __init__(self):
        super().__init__()

        # 프로그레스 바
        self.progress = QProgressBar()
        self.progress.setMinimum(1)
        self.progress.setMaximum(100)


    # 프로그래스 바 초기화 함수
    def reset(self):
        self.progress.setValue(0)

    # 프로그레스 바 증가 함수
    def updateProgress(self):
        current = self.progress.value()
        self.progress.setValue(current + 1)

    # 프로그레스 바 마지막 처리 함수
    def last_progress(self):

        process_bar = self.progress
        current = process_bar.value()
        maxnum = process_bar.maximum()

        process_bar.setValue(current + (maxnum - current))
        print("작업 완료!")

