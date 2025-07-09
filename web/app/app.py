from fastapi import FastAPI, Body, Header
from fastapi.responses import HTMLResponse
from db import get_report, add_report
import verification
from config import config
from rabbit import add_request, get_request
 
app = FastAPI()

# pkg:pypi/requests@2.31.0
get_request()

@app.get("/")
def read_root():
    html_content = "<h2>Hello OSS security testing!</h2>"
    return HTMLResponse(content=html_content)


@app.get("/{manager}:{index}/{name}@{version}")
def read_root(manager: str, index: str, name: str, version: str):
    html_content = verification.verification_purl(manager, index, name, version)
    if html_content:
        return HTMLResponse(content=html_content)
    purl = f"{manager}:{index}/{name}@{version}"
    html_content = get_report(purl)
    if html_content == "added now":
        add_request(purl)
    return HTMLResponse(content=html_content)
