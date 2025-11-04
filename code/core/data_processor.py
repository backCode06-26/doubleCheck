from pathlib import Path
import sys
import json
import config

from code.process.image_processor import ImageProcessor


def dataProcessing(folder_path, json_name):

    # 폴더 생성
    folder_path = Path(folder_path)
    output_folder_path = folder_path / "data"

    output_folder_path.mkdir(parents=True, exist_ok=True)

    # 있다면 기존의 내용 삭제
    for img_name in output_folder_path.iterdir():
        img_name.unlink(missing_ok=True)

    # 대체 이미지 경로
    if getattr(sys, "frozen", False):
        current_path = Path(__file__).resolve().parent
        print(current_path)
    else:
        current_path = Path(
            r"C:\Users\hojin\OneDrive\Desktop\DoubleCheck\dist")
    null_img = current_path / "images" / "null_image.JPG"

    main_images = ImageProcessor.getImagePaths(folder_path)

    # 기본 데이터 형식
    data = {
        "data": [],
        "main": [main_images],
        "blank": [null_img],
        "double": [null_img],
    }

    json_path = folder_path / json_name

    # json 파일 생성
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# 데이터 저장


def saveJson(image_paths, mode="main"):

    # 받은 데이터로 저장
    config.current_json[mode] = image_paths

    # 수정된 데이터로 변경
    with open(config.JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(config.current_json, f, indent=4, ensure_ascii=False)
