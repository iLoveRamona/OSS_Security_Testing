import requests
from bs4 import BeautifulSoup
from packageurl import PackageURL
import re

def get_repo_url(purl_str: str) -> str:
    purl = PackageURL.from_string(purl_str)
    if purl.type != "pypi" or not purl.name or not purl.version:
        raise ValueError("Expected PURL format: pkg:pypi/<name>@<version>")

    name = purl.name.lower().replace('_', '-')
    version = purl.version
    index_url = f"https://pypi.org/simple/{name}/"

    response = requests.get(index_url)
    if response.status_code != 200:
        raise Exception(f"Couldn't find a list of versions of {index_url}")
    soup = BeautifulSoup(response.text, 'html.parser')
    candidates = []
    pattern = rf'.*{version.replace('.', '\\.')}.*\.(tar\.gz|zip)'
    for link in soup.find_all('a'):
        href = link.get('href', '')
        if not href:
            continue
        if re.match(pattern, href):
            candidates.append(href)
    if not candidates:
        raise Exception(f"Coudln't find source code for {purl_str}")
    return candidates[0]
