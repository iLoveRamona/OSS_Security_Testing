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

async def get_request():
    credentials = pika.PlainCredentials(username, password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=ip_server[:ip_server.index(':')],
            credentials=credentials))
    channel = connection.channel()

    def callback(ch, method, properties, body):
        data_dict = json.loads(body) 
        edit_report(data_dict["purl"], data_dict["report"])
        return body

    channel.basic_consume(queue='airflow.end', on_message_callback=callback, auto_ack=True)


    channel.start_consuming()

    connection.close()
