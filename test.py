import os

# CPU 논리 코어(스레드) 개수
available_threads = os.cpu_count()
print(f"사용 가능한 CPU 스레드: {available_threads}")
