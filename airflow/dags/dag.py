from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonVirtualenvOperator
from airflow.decorators import task
from airflow.models import Param

def get_repo_url_from_purl(purl, **kwargs):

    from packageurl import PackageURL
    import os
    import requests
    from time import sleep
    from urllib.parse import urlparse

    def get_repo_url(name, version, retries=3, timeout=5):
        name = name.replace('_','-').lower()
        index = os.getenv('PYPI_INDEX_URL','https://pypi.org')
        url = f"{index}/pypi/{name}/{version}/json"
        backoff = 1
        
        for _ in range(retries):
            try:
                r = requests.get(url, timeout=timeout)
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
                        rel = _get_github_release_url(repo, version)
                        return rel or repo
                    return repo
        if urls:
            return next(iter(urls.values()))
        return homepage
    
    def _get_github_release_url(repo_url, version):
        import requests
        from urllib.parse import urlparse
        
        owner_repo = urlparse(repo_url).path.strip('/')
        repo_url = requests.head(repo_url, allow_redirects=True).url
        base = f'https://api.github.com/repos/{owner_repo}/releases/tags'
        
        for tag in (version, f'v{version}'):
            r = requests.get(f'{base}/{tag}', timeout=5)
            if r.status_code == 200:
                return f'{repo_url}/archive/refs/tags/{tag}.zip'
        return None

    purl = PackageURL.from_string(purl)
    if purl.type != 'pypi' or not purl.name or not purl.version:
        return None
    
    repo_url = get_repo_url(purl.name, purl.version)
    
    return repo_url


def download(repo_url):
    
    import subprocess
    from pathlib import Path
    import shutil
    import zipfile
    import json
    """Скачивает репозиторий по URL из предыдущей задачи"""
    
    if not repo_url:
        raise ValueError("Не получен URL репозитория")
    print('!!!')
    print(repo_url, type(repo_url))
    print('!!!')

    # Подготовка путей
    zip_path = Path("./target.zip")
    extract_dir = Path("./extracted")
    
    # Очистка старых файлов
    shutil.rmtree(extract_dir, ignore_errors=True)
    extract_dir.mkdir()
    print
    # Скачивание архива
    curl_cmd = f"curl -s -L -o {zip_path} {repo_url}"
    curl_result = subprocess.run(
        curl_cmd, shell=True, capture_output=True, text=True, timeout=60
    )
    print(curl_result)
    if curl_result.returncode != 0:
        raise RuntimeError(f"Curl error: {curl_result.stderr}")

    # Распаковка
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    return str(extract_dir)

def scan(target_path):
    import subprocess
    result = subprocess.run(
        ["sudo", "bandit", "-r", str(target_path), "-f", "json"],
        capture_output=True,
        text=True
    )
    
    if result.returncode not in [0, 1]:
        raise RuntimeError(f"Bandit failed: {result.stderr}")
    print('!!!')
    print(result)
    print('!!!')
    return {
        "output": result.stdout,
        "error": result.stderr,
        "return_code": result.returncode
    }

with DAG(
    'oss_flow',
    tags=['package_url']
) as dag:

    get_url_task = PythonVirtualenvOperator(
        task_id="get_url_from_purl",
        python_callable=get_repo_url_from_purl,
        requirements=[
            "requests==2.28.1", 
            "packageurl-python==0.17.1"
        ],
        system_site_packages=False,
        op_kwargs={'purl': '{{ params.purl }}'},
        do_xcom_push=True
    )

    download_task = PythonVirtualenvOperator(
        task_id="download_task",
        python_callable=download,
        system_site_packages=False,
        do_xcom_push=True,
        requirements=["requests==2.28.1"],
        op_kwargs={
            'repo_url': "{{ ti.xcom_pull(task_ids='get_url_from_purl') }}"
        },
    )
    scan_task = PythonVirtualenvOperator(
        task_id="scan_task",
        python_callable=scan,
        system_site_packages=False,
        do_xcom_push=True,
        requirements=["bandit==1.8.5"],
        op_kwargs={
            'target_path': "{{ ti.xcom_pull(task_ids='download_task') }}"
        },
    )

    get_url_task >> download_task >> scan_task
    