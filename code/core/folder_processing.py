import os
import shutil


def image_copys(folder_path, folder_name, image_paths):
    move_folder_path = os.path.join(folder_path, folder_name)

    if not os.path.exists(move_folder_path):
        os.makedirs(move_folder_path)

    for path in image_paths:
        shutil.copy(path, move_folder_path)


def folder_processing(folder_path):
    folder_names = ["double", "blank"]

    for name in folder_names:
        path = os.path.join(folder_path, name)

        # 폴더가 없으면 생성
        if not os.path.exists(path):
            os.makedirs(path)

        for img_name in os.listdir(path):
            os.remove(os.path.join(path, img_name))
