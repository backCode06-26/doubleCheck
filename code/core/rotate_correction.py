import cv2
import numpy as np
from pathlib import Path


def sort_corners(pts):
    pts = np.array(pts, dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    top_left = pts[np.argmin(s)]
    bottom_right = pts[np.argmax(s)]
    top_right = pts[np.argmin(diff)]
    bottom_left = pts[np.argmax(diff)]

    return np.array([top_left, top_right, bottom_right, bottom_left], dtype="float32")


def get_skew_angle(img):
    if img is None:
        print("이미지가 존재하지 않습니다.")
        exit()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    markers = []
    filter_cnt = []
    for contour in contours:
        approx = cv2.approxPolyDP(
            contour, 0.02 * cv2.arcLength(contour, True), True)
        area = cv2.contourArea(contour)

        if len(approx) == 4 and cv2.isContourConvex(approx) and 200 < area < 1000:
            x, y, w, h = cv2.boundingRect(contour)
            quadrate_ratio = w / float(h)
            if 0.8 < quadrate_ratio < 1.2:
                markers.append((x, y))
                filter_cnt.append(contour)

    if len(markers) != 4:
        # cv2.drawContours(img, filter_cnt, -1, (0, 255, 0), 3)

        # plt.figure(figsize=(24, 12))
        # plt.imshow(img)
        # plt.axis("off")
        # plt.show()

        print(f"외곽 정사각형 4개를 찾지 못했습니다. 찾은 개수: {len(markers)}")
        exit()

    return sort_corners(markers)


def correct_skew(img):
    # img_path = Path(img_path)

    # with open(img_path, "rb") as f:
    #     file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
    # img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    sorted_pts = get_skew_angle(img)

    h, w = img.shape[:2]
    dst_pts = np.array([
        [0, 0],
        [w-1, 0],
        [w-1, h-1],
        [0, h-1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(sorted_pts, dst_pts)
    warped = cv2.warpPerspective(img, M, (w, h))

    return warped

# 사용 예시
# corrected_img = correct_skew("omr_image.jpg")
