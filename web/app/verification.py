import re

managers = {"pkg"}

package_index = {"pypi"}

def verification_manager(manager):
    return manager in managers


def verification_versrion(version):
    ver = r"[\d+\.]*\d"
    return re.fullmatch(ver, version)

def verification_index(index):
    return index in package_index

def verification_purl(manager: str, index: str, name: str, version: str):
    html_content = f"<h2>{manager}</h2>\n<h2>{index}</h2>\n<h2>{name}</h2>\n<h2>{version}</h2>\n"
    if not verification_manager(manager):
        html_content = f"<h2>Мы поддерживаем только эти пакетные менеджеры: {" ".join([i for i in managers])}</h2>"
        return html_content
    if not verification_index(index):
        html_content = f"<h2>Мы поддерживаем только эти пакетные индексы: {" ".join([i for i in package_index])}</h2>"
        return html_content
    if not verification_versrion(version):
        html_content = f"<h2>В версии ошибка</h2>"
        return html_content
    return None
