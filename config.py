import multiprocessing

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")  # 허용되는 확장자

all_time = 0

# 검사에 필요한 데이터
json_paths = []
current_json = None

x1, y1, x2, y2 = 0, 0, 0, 0

hash_value = 5
core_count = int(multiprocessing.cpu_count() / 2)
