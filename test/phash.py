import cv2
from PIL import Image
import imagehash

# 이미지 읽기
cv_img1 = cv2.imread(
    r"C:\Users\hojin\OneDrive\Desktop\DoubleCheck\code\system\null_image.JPG")
cv_img2 = cv2.imread(
    r"C:\Users\hojin\OneDrive\Desktop\DoubleCheck\code\system\null_image.JPG")

# BGR -> RGB 변환
cv_img_rgb1 = cv2.cvtColor(cv_img1, cv2.COLOR_BGR2RGB)
cv_img_rgb2 = cv2.cvtColor(cv_img2, cv2.COLOR_BGR2RGB)

# PIL 이미지로 변환
pil_img1 = Image.fromarray(cv_img_rgb1)
pil_img2 = Image.fromarray(cv_img_rgb2)

# pHash 계산
hash1 = imagehash.phash(pil_img1)
hash2 = imagehash.phash(pil_img2)

print("pHash 1:", hash1)
print("pHash 2:", hash2)

# pHash 차이 계산 (해밍 거리)
diff = hash1 - hash2
print("두 이미지의 pHash 차이:", diff)
