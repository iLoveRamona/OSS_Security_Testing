from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from bd import get_report
import verifikation as verifikation
 
app = FastAPI()

# pkg:index/requests@2.31.0

@app.get("/")
def read_root():
    html_content = "<h2>Hello OSS sequryty testing!</h2>"
    return HTMLResponse(content=html_content)


@app.get("/{manager}:{index}/{name}@{version}")
def read_root(manager: str, index: str, name: str, version: str):
    html_content = f"<h2>{manager}</h2>\n<h2>{index}</h2>\n<h2>{name}</h2>\n<h2>{version}</h2>\n"
    if not verifikation.verification_manager(manager):
        html_content = f"<h2>Мы поддерживаем только эти пакетные менеджеры: {" ".join([i for i in verifikation.managers])}</h2>"
        return HTMLResponse(content=html_content)
    if not verifikation.verification_index(index):
        html_content = f"<h2>Мы поддерживаем только эти пакетные индексы: {" ".join([i for i in verifikation.package_index])}</h2>"
        return HTMLResponse(content=html_content)
    if not verifikation.verification_versrion(version):
        html_content = f"<h2>В версии ошибка</h2>"
        return HTMLResponse(content=html_content)
    purl = f"{manager}:{index}/{name}@{version}"
    html_content = get_report(purl)
    return HTMLResponse(content=html_content)
