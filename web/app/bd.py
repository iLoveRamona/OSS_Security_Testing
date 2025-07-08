from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import  Column, Integer, String
import requests
from config import config
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

# def get_jwt():
#     auth_url = f"http://{ip_server}/auth/token"
#     credentials = {
#         "username": "n.i.berukhov",
#         "password": config["airflowPASS"]
#     }
#     response = requests.post(auth_url, json=credentials)
#     return response.json()['access_token']


SessionLocal = sessionmaker(autoflush=False, bind=engine)
db = SessionLocal()

def get_report(purl):
    report = db.query(Reports).filter(Reports.purl == purl).all()
    if len(report):
        report = report[0]
        if report.status == 0:
            return "Wait"
        if report.status == 1:
            return report.report
        if report.status == -1:
            return "Not existst"
    import pika
    username = 'n.i.berukhov'
    password = config["airflowPASS"]

    credentials = pika.PlainCredentials(username, password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=ip_server[:ip_server.index(':')],
            credentials=credentials))
    channel = connection.channel()

    channel.basic_publish(exchange='airflow', routing_key='start', body=purl)

    connection.close()


def add_report(purl, status, report):
    rep = Reports(psurl=purl, status=status, report=report)
    db.add(rep)
    db.commit()
