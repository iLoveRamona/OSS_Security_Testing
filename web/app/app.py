from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse
import bcrypt

from rabbit import add_request
from db import get_report, edit_report
import verification
from config import config, users

app = FastAPI()


# pkg:pypi/requests@2.31.0

@app.post("/api/v1/report/")
def add_report(data = Body()):
    purl = data["purl"]
    passwd = data["passwd"]
    user = data["user"]
    if user and user in users and passwd and not bcrypt.checkpw(passwd.encode(), config["heshPass"].encode()):
        return "lol" 
    edit_report(purl, data["report"])
    return "ok"


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
