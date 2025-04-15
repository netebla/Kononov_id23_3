import hashlib
import itertools
import time
import subprocess
from app.tasks.manager import update_task
from app.celery_worker import celery_app
from app.tasks.manager import STATUS_RUNNING, STATUS_COMPLETED, STATUS_FAILED

@celery_app.task
def brute_force_task(task_id: str, target_hash: str, charset: str, max_length: int, mode: str):
    try:
        print(f"Starting brute force task in mode: {mode}...")

        if mode == "sha256":
            # Брутфорс для простого SHA-256
            found = False
            chars = charset
            total_attempts = sum(len(chars) ** i for i in range(1, max_length + 1))
            attempt_counter = 0

            start_time = time.time()
            timeout = 600  # 10 минут

            for length in range(1, max_length + 1):
                for attempt in itertools.product(chars, repeat=length):
                    password = ''.join(attempt)
                    password_hash = hashlib.sha256(password.encode()).hexdigest()

                    print(f"Trying password: {password}, hash: {password_hash}")
                    print(f"Target hash: {target_hash}")

                    progress = int((attempt_counter / total_attempts) * 100)
                    update_task(task_id, progress=progress)
                    attempt_counter += 1

                    if password_hash == target_hash:
                        print(f"Password found! {password}")
                        update_task(task_id, status=STATUS_COMPLETED, progress=100, result=password)
                        found = True
                        return

                    # Проверка таймаута
                    if time.time() - start_time > timeout:
                        update_task(task_id, status=STATUS_FAILED, progress=100, result=None)
                        return

            if not found:
                update_task(task_id, status=STATUS_FAILED, progress=100, result=None)

        elif mode == "rar":
            # Брутфорс для RAR архива через внешний процесс
            print("Starting RAR password cracking...")

            # Здесь нужен подготовленный файл с хешем и словарь
            command = [
                "john",
                "--wordlist=your_wordlist.txt",  # 👉 путь к твоему словарю
                "your_hash_file.hash"            # 👉 путь к файлу с хешем
            ]

            result = subprocess.run(command, capture_output=True, text=True)

            print(result.stdout)

            if "PASSWORD CRACKED" in result.stdout or "password hash cracked" in result.stdout:
                update_task(task_id, status=STATUS_COMPLETED, progress=100, result=result.stdout)
            else:
                update_task(task_id, status=STATUS_FAILED, progress=100, result=None)

        else:
            print("Unknown mode!")
            update_task(task_id, status=STATUS_FAILED, progress=0, result=None)

    except Exception as e:
        print(f"Error occurred: {e}")
        update_task(task_id, status=STATUS_FAILED, progress=0, result=None)