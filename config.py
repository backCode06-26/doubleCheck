import multiprocessing

OUTPUT_FOLDER_PATH = None
all_time = 0

# 파일 경로 저장에 필요한 데이터
JSON_PATH = None
current_json = None

# 검사에 필요한 데이터
FOLDER_PATH = None
hash_value = 5
core_count = multiprocessing.cpu_count() - 1
