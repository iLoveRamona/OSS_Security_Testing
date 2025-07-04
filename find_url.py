import os
import requests
from time import sleep
from urllib.parse import urlparse
from packageurl import PackageURL

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
                sleep(backoff); backoff *= 2
            else:
                return None
        except requests.RequestException:
            sleep(backoff); backoff *= 2
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
    owner_repo = urlparse(repo_url).path.strip('/')
    repo_url = requests.head(repo_url, allow_redirects=True).url
    base = f'https://api.github.com/repos/{owner_repo}/releases/tags'
    for tag in (version, f'v{version}'):
        r = requests.get(f'{base}/{tag}', timeout=5)
        if r.status_code == 200:
            return f'{repo_url}/archive/refs/tags/{tag}.zip'
    return None

def get_repo_url_from_purl(purl_str, **kwargs):
    purl = PackageURL.from_string(purl_str)
    if purl.type != 'pypi' or not purl.name or not purl.version:
        return None
    return get_repo_url(purl.name, purl.version, **kwargs)

print(get_repo_url_from_purl('pkg:pypi/pandas@2.3.0'))