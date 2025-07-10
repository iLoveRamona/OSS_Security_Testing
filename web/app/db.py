from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import  Column, Integer, String, Index

from config import config

ip_server = config["ipServer"]


SQLALCHEMY_DATABASE_URL = "postgresql://pg:root@db_reports/oss_security_testing"
engine = create_engine(SQLALCHEMY_DATABASE_URL)


class Base(DeclarativeBase): pass


class Reports(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    purl = Column(String, index=True)
    status = Column(Integer)
    report = Column(String)


reports_purl_index = Index('purl_idx', Reports.purl)
Base.metadata.create_all(bind=engine)


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
    add_report(purl, 0, "")
    return "added now"

def add_report(purl, status, report):
    rep = Reports(purl=purl, status=status, report=report)
    db.add(rep)
    db.commit()

def edit_report(purl, report):
    reports = db.query(Reports).filter(Reports.purl == purl).all()
    reports = reports[0]
    if report:
        reports.status = 1
        reports.report = report
    else:
        reports.status = -1
    db.commit()
