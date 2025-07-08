import shutil
import zipfile
from pathlib import Path
def download_repo(repo_url):
    """Скачивание репозитория"""
    if not repo_url:
        raise ValueError("Repository URL not provided")
    
    # Подготовка путей
    zip_path = Path("/tmp/target.zip")
    extract_dir = Path("/tmp/extracted")
    
    # Очистка старых файлов
    shutil.rmtree(extract_dir, ignore_errors=True)
    extract_dir.mkdir()
    
    # Скачивание архива
    curl_cmd = f"curl -s -L -o {zip_path} {repo_url}"
    curl_result = subprocess.run(
        curl_cmd, shell=True, capture_output=True, text=True
    )
    
    if curl_result.returncode != 0:
        raise RuntimeError(f"Curl error: {curl_result.stderr}")

    # Распаковка
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    return str(extract_dir)