import pika
import json
import os
import requests
from packageurl import PackageURL
from pathlib import Path
import shutil
import zipfile
import subprocess
from urllib.parse import urlparse
from time import sleep

def get_repo_url(package_name, package_version):
    """Получение URL репозитория по имени и версии пакета"""
    name = package_name.replace('_','-').lower()
    index = os.getenv('PYPI_INDEX_URL','https://pypi.org')
    url = f"{index}/pypi/{name}/{package_version}/json"
    backoff = 1
    
    for _ in range(3):  # retries
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                break
            if 500 <= r.status_code < 600:
                sleep(backoff)
                backoff *= 2
            else:
                return None
        except requests.RequestException:
            sleep(backoff)
            backoff *= 2
    else:
        return None

    info = data['info']
    urls = info.get('project_urls') or {}
    homepage = info.get('home_page')

    for provider in ('github.com','gitlab.com','bitbucket.org'):
        for u in urls.values():
            if provider in urlparse(u).netloc:
                repo = u.split('/archive/')[0].split('.tar.gz')[0]
                if 'github.com' in provider:
                    rel = get_github_release_url(repo, package_version)
                    return rel or repo
                return repo
    return next(iter(urls.values())) if urls else homepage

def get_github_release_url(repo_url, version):
    """Получение URL релиза на GitHub"""
    owner_repo = urlparse(repo_url).path.strip('/')
    repo_url = requests.head(repo_url, allow_redirects=True).url
    base = f'https://api.github.com/repos/{owner_repo}/releases/tags'
    
    for tag in (version, f'v{version}'):
        r = requests.get(f'{base}/{tag}', timeout=5)
        if r.status_code == 200:
            return f'{repo_url}/archive/refs/tags/{tag}.zip'
    return None

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