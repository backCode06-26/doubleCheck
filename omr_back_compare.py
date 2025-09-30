import os
import cv2
import matplotlib.pyplot as plt
from extract_region import crop_roi
from blank_checker import is_blank_page
from skimage.metrics import structural_similarity as ssim

image_extensions = (".png", ".jpg", ".jpeg", ".bmp")
image_files = []


def omr_back_compare(folder_path, add_image):
    if folder_path:
        image_files = os.listdir(folder_path)

    for i in range(1, len(image_files), 2):

        first_path = os.path.join(
            folder_path, image_files[i]).replace("\\", "/")
        if is_blank_page(first_path):

            print(image_files[i])
            print("백지답안 입니다.")
            add_image(image_files[i], 'blank')
            continue

        for j in range(i+2, len(image_files), 2):

            second_path = os.path.join(
                folder_path, image_files[j]).replace("\\", "/")
            if is_blank_page(second_path):

                print(image_files[j])
                print("백지답안 입니다.")
                add_image(image_files[j], 'blank')
                continue

            print("백지 답안인지 검사하는 중입니다.")

            first_img = crop_roi(first_path)
            second_img = crop_roi(second_path)

            print("이미지 전처리를 진행하는 중입니다.")

            h, w = first_img.shape[:2]
            second_img = cv2.resize(second_img, (w, h))

            if first_img is None or second_img is None:
                print("이미지를 찾을 수 없습니다.")
                exit()

            ssim_score, ssim_map = ssim(first_img, second_img, full=True)

            print("중복 답안인지 검사하는 중입니다.")

            if ssim_score >= 0.9:
                print(image_files[i])
                print(image_files[j])

                print("중복답안 입니다.")

                add_image(image_files[i], 'double')
                add_image(image_files[j], 'double')
            else:
                print(image_files[i])
                print(image_files[j])

                print("이미지가 중복되지 않습니다.")

            print("\n\n", f"이미지 유사도: {ssim_score}")

            # plt.imshow(ssim_map, cmap='gray')
            # plt.axis("off")
            # plt.colorbar()
            # plt.show()
