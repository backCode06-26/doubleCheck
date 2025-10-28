from PySide6.QtCore import QObject, Signal, QRunnable, Slot
from concurrent.futures import ThreadPoolExecutor

import os
import cv2
import config
import numpy as np
import imagehash
from PIL import Image
from multiprocessing import Pool
from code.core.blank_checker import isBlankImage
from code.core.rotate_correction import correct_skew
from code.core.data_processor import saveJson

class ImagePreprocessingSingnals(QObject):
    progress = Signal(str)
    error = Signal(str)
    complete = Signal()
    finished = Signal()

def run_processing(image_paths):
    black_image_paths = []
    with ThreadPoolExecutor(max_workers=config.core_count) as executor:
        results = list(executor.map(ImageProcessor._process_single_image, image_paths))
    saveJson(results, "data")
            
class ImageProcessor:

    @staticmethod
    def getSafeImgLoad(img_path):
        with open(img_path, "rb") as f:
            file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        return img

    @staticmethod
    def cv2ToPIL(img):
        cv_img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(cv_img_rgb)
        return pil_img
    
    @staticmethod
    def _process_single_image(path):
        img = ImageProcessor.getSafeImgLoad(path)

        file_name = os.path.basename(path)
        ouput_folder_path = config.OUTPUT_FOLDER_PATH

        pre_img = correct_skew(img)
        
        output_path = os.path.join(ouput_folder_path, file_name)
        print(output_path)
        ImageProcessor.saveImage(pre_img, output_path)

        image_hash = ImageProcessor.getImageHash(pre_img)
        is_blank = isBlankImage(pre_img)

        return {
            "pre_img" : output_path, 
            "image_hash" : image_hash, 
            "is_blank" : is_blank
        }
    @staticmethod
    def getImageHash(img):
        pil_img = ImageProcessor.cv2ToPIL(img)
        hash_value = imagehash.phash(pil_img)
        return hash_value
    
    @staticmethod
    def saveImage(img, output_path):
        pil_img = ImageProcessor.cv2ToPIL(img)
        img_gray = pil_img.convert('L')
        img_gray.save(output_path)