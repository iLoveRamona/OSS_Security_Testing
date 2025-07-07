from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import  Column, Integer, String
import requests
from dotenv import dotenv_values

config = dotenv_values(".env")

ip_server = "51.250.44.45:8080"


SQLALCHEMY_DATABASE_URL = "postgresql://pg:root@db_reports/oss_security_testing"
engine = create_engine(SQLALCHEMY_DATABASE_URL)


class Base(DeclarativeBase): pass


class Reports(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    purl = Column(String, index=True)
    status = Column(Integer)
    report = Column(String)

Base.metadata.create_all(bind=engine)

def get_jwt():
    auth_url = f"http://{ip_server}/auth/token"
    credentials = {
        "username": "n.i.berukhov",
        "password": config["airflowPASS"]
    }
    response = requests.post(auth_url, json=credentials)
    return response.json()['access_token']


SessionLocal = sessionmaker(autoflush=False, bind=engine)
db = SessionLocal()

def get_report(purl):
    report = db.query(Reports).filter(Reports.purl == purl).all()
    if len(report):
        return report[0].report
    url = f"http://{ip_server}/api/v2/dags/oss_flow/dagRuns"
    headers = {"Authorization": f"Bearer {get_jwt()}",
               "Content-Type": "application/json"}
    data = {
        "logical_date": None,
        "conf": {"purl": f"{purl}"},
    }
    response = requests.post(
        url, 
        headers=headers, 
        json=data
    )
    print(response.status_code)
    print(response.json())


def add_report(purl, report):
    rep = Reports(purl=purl, report=report)
    db.add(rep)
    db.commit()

