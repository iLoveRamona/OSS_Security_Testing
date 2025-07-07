from fastapi import FastAPI, Body, Header
from fastapi.responses import HTMLResponse, HTTPResponse
from bd import get_report, add_report
import verifikation as verifikation
from config import config
 
app = FastAPI()

# pkg:index/requests@2.31.0

@app.get("/")
def read_root():
    html_content = "<h2>Hello OSS security testing!</h2>"
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


@app.post("/api/airflow")
def create_person(data = Body()):
    if data['secret'] == config['passwd']:
        add_report(data["purl"], data["report"])
        return HTTPResponse(200)
    return HTTPResponse(401)
