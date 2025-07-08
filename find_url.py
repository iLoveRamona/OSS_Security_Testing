import requests
from bs4 import BeautifulSoup
from packageurl import PackageURL

def get_repo_url_from_purl(purl_str: str) -> str:
    purl = PackageURL.from_string(purl_str)
    if purl.type != "pypi" or not purl.name or not purl.version:
        raise ValueError("Ожидается PURL вида pkg:pypi/<name>@<version>")

    name = purl.name.lower().replace('_', '-')
    version = purl.version
    index_url = f"https://pypi.org/simple/{name}/"

    response = requests.get(index_url)
    if response.status_code != 200:
        raise Exception(f"Не удалось получить список версий с {index_url}")
    soup = BeautifulSoup(response.text, 'html.parser')
    candidates = []
    for link in soup.find_all('a'):
        href = link.get('href', '')
        if not href:
            continue
        if f"{name}-{version}.tar.gz" in href or f"{name}-{version}.zip" in href:
            candidates.append(href)
    if not candidates:
        raise Exception(f"Не найден исходный архив для {purl_str}")
    return candidates[0]