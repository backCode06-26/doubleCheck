import cv2
import numpy as np

# 1. 이미지 읽기 & 그레이스케일
def phash_cv(img):

    if len(img.shape) != 2:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. 크기 조정
    img = cv2.resize(img, (32, 32))

    # 3. DCT 적용(저주파(큰 구조), 고주파(세부 구조))
    dct = cv2.dct(np.float32(img))

    # 4. 상위 8x8 영역 추출 (저주파 추출)
    dct_roi = dct[:8, :8]

    # 5. 평균값 기준으로 0/1 결정
    avg = dct_roi.mean() # 저주파의 평균값 구하기

    # 저주파 영역에서 평균값보다 크면 True 작으면 False로 재구성합니다.
    hash_array = dct_roi > avg

    # 6. 64비트 해시 생성 (재구성된 배열을 1과 0으로 다시 재구성합니다.)
    hash_str = ''.join(['1' if x else '0' for x in hash_array.flatten()])
    hash = int(hash_str, 2)
    return hash

def compare_image(hash1, hash2):
    diff = bin(hash1 ^ hash2).count("1")
    similarity = 1 - (diff / 64)
    return similarity


first_img = cv2.imread("system/null_image.JPG")
secoend_img = cv2.imread("system/null_image.JPG")

hash1 = phash_cv(first_img)
hash2 = phash_cv(secoend_img)

print(compare_image(hash1, hash2))