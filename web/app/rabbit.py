import pika
import json

from config import config
from db import edit_report

username = config["airflowUser"]
password = config["airflowPASS"]
ip_server = config["ipSerwer"]

def add_request(purl):
    credentials = pika.PlainCredentials(username, password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=ip_server[:ip_server.index(':')],
            credentials=credentials))
    channel = connection.channel()
    body = {
        "purl":purl
    }
    channel.basic_publish(exchange='airflow', routing_key='start', body=json.dumps(body))

    connection.close()
