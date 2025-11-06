import multiprocessing

all_time = 0

# 검사에 필요한 데이터
json_paths = []
current_json = None

top = 0
bottom = 0
right = 0
left = 0

hash_value = 5
core_count = int(multiprocessing.cpu_count() / 2)
