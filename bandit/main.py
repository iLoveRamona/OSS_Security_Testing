import os
import zipfile
import shutil
import subprocess
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Bandit Security Scanner")


TMP_DIR = "./tmp"
Path(TMP_DIR).mkdir(exist_ok=True)

class ScanRequest(BaseModel):
    url: str  # URL ZIP-архива с Python-кодом

def run_bandit(target_path: Path) -> dict:
    """Запускает Bandit для указанной директории"""
    result = subprocess.run(
        ["bandit", "-r", str(target_path), "-f", "json"],
        capture_output=True,
        text=True
    )
    
    if result.returncode not in [0, 1]:
        raise RuntimeError(f"Bandit failed: {result.stderr}")
    
    return {
        "output": result.stdout,
        "error": result.stderr,
        "return_code": result.returncode
    }

@app.post("/scan")
async def scan_code(request: ScanRequest):
    """
    Скачивает ZIP-архив, распаковывает и запускает Bandit
    
    Пример запроса:
    {
        "url": "https://github.com/user/repo/archive/main.zip"
    }
    """
    try:
        # Подготовка путей
        zip_path = Path(TMP_DIR) / "target.zip"
        extract_dir = Path(TMP_DIR) / "extracted"
        
        # Очистка старых файлов
        shutil.rmtree(extract_dir, ignore_errors=True)
        extract_dir.mkdir()

        # Скачивание архива
        curl_cmd = f"curl -s -L -o {zip_path} {request.url}"
        curl_result = subprocess.run(
            curl_cmd, shell=True, capture_output=True, text=True, timeout=60
        )
        if curl_result.returncode != 0:
            raise HTTPException(500, f"Curl error: {curl_result.stderr}")

        # Распаковка
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Запуск Bandit
        bandit_result = run_bandit(extract_dir)

        # Очистка (можно закомментировать для отладки)
        shutil.rmtree(extract_dir)
        zip_path.unlink()

        return {
            "status": "success",
            "bandit_results": bandit_result["output"],
            "error": bandit_result["error"],
            "scan_status": "passed" if bandit_result["return_code"] == 0 else "issues_found"
        }

    except zipfile.BadZipFile:
        raise HTTPException(400, "Invalid ZIP archive")
    except Exception as e:
        shutil.rmtree(extract_dir, ignore_errors=True)
        if zip_path.exists():
            zip_path.unlink()
        raise HTTPException(500, str(e))