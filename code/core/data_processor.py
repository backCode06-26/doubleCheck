import os
import sys
import json
import config


def dataProcessing(folder_path):

    # 폴더 생성
    output_folder_path = os.path.join(folder_path, "data")

    # json 파일 경로
    json_path = os.path.join(output_folder_path, "config.json")

    config.FOLDER_PATH = folder_path
    config.JSON_PATH = json_path
    config.OUTPUT_FOLDER_PATH = output_folder_path

    # 폴더가 없으면 생성
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    # 있다면 기존의 내용 삭제
    for img_name in os.listdir(output_folder_path):
        os.remove(os.path.join(output_folder_path, img_name))

    # 대체 이미지 경로
    if getattr(sys, "frozen", False):
        current_path = os.path.dirname(os.path.abspath(sys.executable))
    else:
        current_path = r"C:\Users\hojin\OneDrive\Desktop\DoubleCheck\dist"
    null_img = os.path.join(
        current_path, "images", "null_image.JPG").replace("\\", "/")

    # 기본 데이터 형식
    data = {
        "data": [],
        "main": [null_img],
        "blank": [null_img],
        "double": [null_img],
    }

    # json 파일 생성
    with open(config.JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(config.current_json, f, indent=4, ensure_ascii=False)

    config.current_json = data

# 데이터 저장


def saveJson(image_paths, mode="main"):

    # 받은 데이터로 저장
    config.current_json[mode] = image_paths

    # 수정된 데이터로 변경
    with open(config.JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(config.current_json, f, indent=4, ensure_ascii=False)
