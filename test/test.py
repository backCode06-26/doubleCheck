import cv2
import numpy as np

img = np.ones((500, 500, 3), dtype=np.uint8) * 255

color = (0, 0, 0)
thickness = 5

cv2.line(img, (0, 0), (499, 499), color, thickness)
cv2.line(img, (499, 0), (0, 499), color, thickness)

# 3. 결과 보여주기
cv2.imwrite("null_image.JPG", img)
