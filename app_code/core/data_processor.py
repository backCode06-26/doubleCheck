from pathlib import Path
import sys
import json


def precompute_image_features(folder_path, json_path, image_pahts):

    # 폴더 생성
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
            "C:/Users/hojin/OneDrive/Desktop/DoubleCheck/dist")
    null_img = str(current_path / "images" / "null_image.JPG")

    # 기본 데이터 형식
    data = {
        "data": [],
        "main": image_pahts,
        "blank": [null_img],
        "double": [null_img],
    }

    # json 파일 생성
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def read_json(json_path, mode="main"):
    with open(json_path, "r", encoding="utf-8") as f:
        load = json.load(f)

    return load[mode]


def update_json(json_path, results, mode="main"):

    # json 내용 읽기
    with open(json_path, "r", encoding="utf-8") as f:
        load = json.load(f)

    # 내용 수정
    load[mode] = results

    # json 파일 저장
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(load, f, indent=4, ensure_ascii=False)
