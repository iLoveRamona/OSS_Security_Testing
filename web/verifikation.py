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
