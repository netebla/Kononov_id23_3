import subprocess
import os

def create_wordlist(wordlist_path):
    passwords = [
        "123456", "password", "abc", "qwerty",
        "test", "admin", "1234", "abc123"
    ]
    with open(wordlist_path, "w") as f:
        for password in passwords:
            f.write(password + "\n")
    print(f"Wordlist created at {wordlist_path}")

def extract_rar_hash(rar_path, hash_output_path):
    rar2john_path = "/opt/homebrew/Cellar/john-jumbo/1.9.0_1/share/john/rar2john"  
    if not os.path.exists(rar_path):
        print(f"RAR file not found: {rar_path}")
        return
    with open(hash_output_path, "w") as f:
        subprocess.run([rar2john_path, rar_path], stdout=f)
    print(f"Hash extracted to {hash_output_path}")

if __name__ == "__main__":
    # Папка для файлов
    os.makedirs("files", exist_ok=True)

    # Генерация словаря
    create_wordlist("files/your_wordlist.txt")

    # Генерация файла хеша из архива
    rar_path = "/Users/kirillkononov/Documents/2 курс/Практикум/Лаба_3_семестр/bruteforce_project/files/testfile — копия.rar" 
    hash_output_path = "files/your_hash_file.hash"
    extract_rar_hash(rar_path, hash_output_path)