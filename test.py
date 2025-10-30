import os
import cv2
import numpy as np  # <-- np import 필수!
from code.process.image_processor import ImageProcessor

# ... (getSafeImgLoad 함수 정의) ...

test_path = 'C:/Users/hojin/OneDrive/Desktop/이중급지 테스트용 답안/1000202.JPG'

# 1. 파일 존재 확인 (오류 메시지 방지를 위해)
if not os.path.exists(test_path):
    print("오류: 파일 경로를 찾을 수 없습니다.")
else:
    try:
        img = ImageProcessor.getSafeImgLoad(test_path)
        if img is not None:
            print(f"이미지 로드 성공! 크기: {img.shape}")
        else:
            print("이미지 로드 실패: cv2.imdecode에서 None 반환")
    except Exception as e:
        print(f"이미지 로드 중 예외 발생: {e}")
