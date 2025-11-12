from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QPushButton, QLabel, QFileDialog, QHBoxLayout, QDialog
)
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QImage

import config

import cv2
from app_code.core.rotate_correction import correct_skew
from app_code.process.image_processor import ImageProcessor


class ImageCropWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("QLabel { background-color: #2b2b2b; }")
        self.setMinimumSize(400, 300)
        
        self.original_pixmap = None
        self.scaled_pixmap = None
        self.crop_rect = QRect()
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False
        
    def load_image(self, image):
        self.original_pixmap = image
        self.update_display() # 이미지 디스플레이 업데이트
        self.crop_rect = QRect() # 사각형 객체 초기화
        
    def update_display(self):
        # 기본 이미지가 존재한다면
        if self.original_pixmap:
            # 이미지를 자름
            self.scaled_pixmap = self.original_pixmap.scaled(
                # 현재 위젯의 크기를 지정함
                self.size(),
                # 비율을 유지하며 크기 조절
                Qt.KeepAspectRatio, 
                # 이미지 축소 시 부드럽게 조절
                Qt.SmoothTransformation
            )
            self.update()
    
    # 이미지를 그리는 이벤트, 
    # 위젯이 처음 생성될때 크기가 변경될때, update()가 호출될때 실행
    def paintEvent(self, event):
        # 이벤트 상속
        super().paintEvent(event)

        # 스케일된 이미지가 존재한다면
        if self.scaled_pixmap:
            # 그리기 도구 생성
            painter = QPainter(self)
            
            # 이미지 중앙에 그리기
            x = (self.width() - self.scaled_pixmap.width()) // 2
            y = (self.height() - self.scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, self.scaled_pixmap)
            
            # 크롭 영역 그리기, 그롭 영역이 존재한다면 
            if not self.crop_rect.isNull():
                # 4개의 영역으로 나누어 어둡게 처리
                widget_rect = self.rect()
                
                # 위쪽 영역
                top_rect = QRect(widget_rect.left(), widget_rect.top(), 
                                widget_rect.width(), self.crop_rect.top() - widget_rect.top())
                painter.fillRect(top_rect, QColor(0, 0, 0, 150))
                
                # 아래쪽 영역
                bottom_rect = QRect(widget_rect.left(), self.crop_rect.bottom(),
                                   widget_rect.width(), widget_rect.bottom() - self.crop_rect.bottom())
                painter.fillRect(bottom_rect, QColor(0, 0, 0, 150))
                
                # 왼쪽 영역
                left_rect = QRect(widget_rect.left(), self.crop_rect.top(),
                                 self.crop_rect.left() - widget_rect.left(), self.crop_rect.height())
                painter.fillRect(left_rect, QColor(0, 0, 0, 150))
                
                # 오른쪽 영역
                right_rect = QRect(self.crop_rect.right(), self.crop_rect.top(),
                                  widget_rect.right() - self.crop_rect.right(), self.crop_rect.height())
                painter.fillRect(right_rect, QColor(0, 0, 0, 150))
                
                # 선택 영역 테두리 (초록색)
                pen = QPen(QColor(0, 255, 0), 3, Qt.SolidLine)
                painter.setPen(pen)
                # 선택 영역 테두리 그리기
                painter.drawRect(self.crop_rect)
    
    # 마우스를 눌렀을 때
    def mousePressEvent(self, event):
        # 왼쪽 버튼을 누르며, 스케일된 이미지가 있을 때
        if event.button() == Qt.LeftButton and self.scaled_pixmap:
            # 마우스의 시작했을 때, 끝냈을 때 x, y 좌표를 가져옵니다.
            self.start_point = event.position().toPoint()
            self.end_point = event.position().toPoint()

            # 마우스를 움직이고 있는 상태 지정
            self.is_drawing = True
            
    # 마우스를 움직일 때
    def mouseMoveEvent(self, event):
        # 마우스로 그리고 있는 상태라면
        if self.is_drawing:
            # 마우스의 현재 위치를 가져옵니다.
            self.end_point = event.position().toPoint()
            # 시작점과 끝점을 기준으로 사각형 영역을 만듭니다.
            self.crop_rect = QRect(self.start_point, self.end_point).normalized()
            # 다시 그리라고 요청함
            self.update()
    
    # 마우스를 땠을 때
    def mouseReleaseEvent(self, event):
        # 왼쪽 버튼을 뗐을 때
        if event.button() == Qt.LeftButton:
            # 움직이는 상태를 해제합니다.
            self.is_drawing = False
            
    def get_cropped_image(self):
        if self.original_pixmap and not self.crop_rect.isNull():
            # 스케일된 좌표를 원본 이미지 좌표로 변환

            # 이미지의 중앙 위치를 계산함
            x_offset = (self.width() - self.scaled_pixmap.width()) // 2
            y_offset = (self.height() - self.scaled_pixmap.height()) // 2
            
            # 전체 이미지 기준의 크롭 좌표를 이미지 기준으로 변환
            crop_x = self.crop_rect.x() - x_offset
            crop_y = self.crop_rect.y() - y_offset
            
            # 기존 이미지와 스케일된 이미지의 비율을 계산
            scale_x = self.original_pixmap.width() / self.scaled_pixmap.width()
            scale_y = self.original_pixmap.height() / self.scaled_pixmap.height()
            
            # 원본 이미지 기준의 크롭 사각형 계산
            orig_crop_rect = QRect(
                int(crop_x * scale_x),
                int(crop_y * scale_y),
                int(self.crop_rect.width() * scale_x),
                int(self.crop_rect.height() * scale_y)
            )
            
            # 좌표 정보 반환 (pixmap, x1, y1, x2, y2)
            x1 = orig_crop_rect.x()
            y1 = orig_crop_rect.y()
            x2 = orig_crop_rect.x() + orig_crop_rect.width()
            y2 = orig_crop_rect.y() + orig_crop_rect.height()
            
            return self.original_pixmap.copy(orig_crop_rect), x1, y1, x2, y2
        return None, 0, 0, 0, 0
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()


class ImageCropPanel(QDialog):
    def __init__(self, image_path):
        super().__init__()
        self.setModal(True)

        self.setWindowTitle("이미지 크롭 도구")
        self.setGeometry(100, 100, 600, 900)

        # 레이아웃
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 크롭 위젯
        self.crop_widget = ImageCropWidget()
        self.crop_widget.setGeometry(100, 100, 1200, 900)
        self.load_image(image_path)
        layout.addWidget(self.crop_widget, 1)

        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 10, 10, 10)
        button_layout.setSpacing(5)

        # 크롭 버튼
        self.crop_btn = QPushButton("크롭하기")
        self.crop_btn.clicked.connect(self.crop_image)
        self.crop_btn.setEnabled(True)
        button_layout.addWidget(self.crop_btn)

        layout.addLayout(button_layout)

        self.cropped_pixmap = None

    def cv2_to_qpixmap(self, cv_img):
        """OpenCV 이미지를 그레이스케일 QPixmap으로 변환"""
        # 컬러든 그레이스케일이든 무조건 그레이로 변환
        if len(cv_img.shape) == 3:  # 컬러 이미지인 경우
            cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        
        # 그레이스케일 처리
        height, width = cv_img.shape
        qimg = QImage(cv_img.data, width, height, width, QImage.Format_Grayscale8)
        return QPixmap.fromImage(qimg)

    def load_image(self, image_path):
        cv_img = ImageProcessor.get_safe_load_img(image_path)
        cv_correct_img = correct_skew(cv_img)

        q_image = self.cv2_to_qpixmap(cv_correct_img)
        self.crop_widget.load_image(q_image)

    def crop_image(self):
        result = self.crop_widget.get_cropped_image()
        self.cropped_pixmap, x1, y1, x2, y2 = result

        if self.cropped_pixmap:
            self.crop_widget.original_pixmap = self.cropped_pixmap
            self.crop_widget.update_display()
            self.crop_widget.crop_rect = QRect()

            config.x1 = x1
            config.y1 = y1
            config.x2 = x2
            config.y2 = y2

            self.accept()  # 모달 대화상자 종료