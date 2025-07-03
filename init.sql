CREATE SEQUENCE IF NOT EXISTS report_id START WITH 1;
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY DEFAULT nextval('report_id'),
    purl TEXT,
    report TEXT
);
