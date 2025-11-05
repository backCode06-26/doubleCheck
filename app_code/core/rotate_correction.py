import cv2
from matplotlib.path import Path
import numpy as np
import os
import matplotlib.pyplot as plt


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

        if cv2.isContourConvex(approx) and 300 < area < 1000 and len(approx) <= 4:
            x, y, w, h = cv2.boundingRect(contour)
            quadrate_ratio = w / float(h)
            if 0.5 < quadrate_ratio < 1.5:
                markers.append((x, y))
                filter_cnt.append(contour)

    if len(markers) != 4:

        # for contour in contours:

        #     approx = cv2.approxPolyDP(
        #         contour, 0.02 * cv2.arcLength(contour, True), True)
        #     area = cv2.contourArea(contour)
        #     x, y, w, h = cv2.boundingRect(contour)
        #     quadrate_ratio = w / float(h)

        #     print(
        #         f"approx_count: {len(approx)}, {cv2.isContourConvex(approx)}")
        #     print(f"area: {area}, x: {x}, y: {y}")
        #     print(f"squre_ratio: {quadrate_ratio}")

        #     img_copy = img.copy()  # 원본 보호

        #     cv2.drawContours(img_copy, [contour], -1, (0, 255, 0), 3)

        #     # BGR → RGB 변환 (Matplotlib용)
        #     img_rgb = cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB)

        #     plt.figure(figsize=(12, 8))
        #     plt.imshow(img_rgb)
        #     plt.axis("off")
        #     plt.title(f"컨투어 위치: ({x}, {y}) / 면적: {area}")
        #     plt.show()

        # cv2.drawContours(img, filter_cnt, -1, (0, 255, 0), 3)

        # plt.figure(figsize=(24, 12))
        # plt.imshow(img)
        # plt.axis("off")
        # plt.show()

        print(f"외곽 정사각형 4개를 찾지 못했습니다. 찾은 개수: {len(markers)}")
        exit()

    return sort_corners(markers)


def correct_skew(img):

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
