import cv2
import numpy as np
from collections import namedtuple
from code.core.rotate_correction import correct_skew

# 자를 위치 관련 데이터
PointRect = namedtuple('PointRect', ['x1', 'x2', 'y1', 'y2'])
points = []


# 점선을 하나의 선으로 만드는 함수
def points_to_lines(dotted_line_points):
    dotted_line_points.sort(key=lambda point: point[1])

    lines = []
    current_line = []
    threshold = 2
    for point in dotted_line_points:

        x, y = point

        if not current_line:
            current_line.append([x, y])

        if (abs(current_line[-1][1] - y) <= threshold):
            current_line.append([x, y])
        else:
            if (len(current_line) > 10):
                lines.append(current_line)
            current_line = [[x, y]]

    global points
    points = []

    lines = [np.array(line) for line in lines]

    for line in lines:
        xs = line[:, 0]
        ys = line[:, 1]

        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        points.append(PointRect(x1=min_x, x2=max_x, y1=min_y, y2=max_y))


# 겹치는 선을 병합하는 함수
def merge_rects(rects):
    rects.sort(key=lambda r: r.y1)
    merged = []

    merged.append(rects[0])
    merged.append(rects[-1])
    return merged


def crop_roi(img_path):

    # 이미지의 기울기를 보정합니다.
    img = correct_skew(img_path)

    x, y = img[:2]

    # 이미지가 있는지 확인합니다.
    if img is None:
        print("이미지가 존재하지 않습니다.")
        exit()

    # 이미지를 전처리합니다.
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # 이미지의 모든 윤곽선을 가져옵니다.
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 이미지에서 가져온 윤곽선의 넓이와 가로, 세로 길이로 선인지 판단합니다.
    global points

    dotted_line_points = []

    lines_xy = []
    points_xy = []
    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)

        # 직선 판단
        if 10 < area > 3000 and w < 2000 and h < 10:
            points.append(PointRect(x1=x, x2=x+w, y1=y, y2=y+h))
            lines_xy.append(contour)

        # 점선 판단
        if 35 <= area <= 45 and 5 <= w <= 100 and 5 <= h <= 100:
            dotted_line_points.append([x, y])
            points_xy.append(contour)

    # 이미지의 점선을 추출하기 위해서 각 점과 조금씩 차이 안나는 것만 모아서 선을 만들 재료를 구합니다.
    if (len(points) > 2):
        points = merge_rects(points)

        # print(len(points))
        # print(points)

    if (len(points) < 2):
        points_to_lines(dotted_line_points)

    # 구한 데이터로 잘라낼 이미지의 좌표를 구합니다.
    points.sort(key=lambda p: p.y1)

    top_point = points[0]
    bottom_point = points[1]

    x1, x2 = top_point.x1, top_point.x2
    y1 = top_point.y1
    y2 = bottom_point.y2

    roi = gray[y1:y2, x1:x2]

    return roi
