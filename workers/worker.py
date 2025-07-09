import pika
import json
import os
import requests
from packageurl import PackageURL
import shutil
from urllib.parse import urlparse
from time import sleep
from download import download_repo
from find_url import get_github_release_url
from config import *
from find_url import get_repo_url
from scan import scan_repo
from download import download_repo


def callback(report, purl):
    payload = {
        'report': report,
        'passwd': WEB_SECRET,
        'purl': purl,
        'user': WEB_USER
    }
    try:
        response = requests.post(f"{WEB_URL}/api/v1/report", json=payload)
        response.raise_for_status()
        print(f"Report for {purl} sent successfully")
    except requests.RequestException as e:
        print(f"Failed to send report for {purl}: {e}")

def process_purl(purl_str):
    """Обработка PURL"""
    purl_obj = PackageURL.from_string(purl_str)
    if purl_obj.type != 'pypi' or not purl_obj.name or not purl_obj.version:
        raise ValueError("Invalid PyPI package URL")
    
    # Получение URL репозитория
    repo_url = get_repo_url(purl_obj.name, purl_obj.version)
    if not repo_url:
        raise ValueError("Could not determine repository URL")
    
    # Скачивание репозитория
    repo_path = download_repo(repo_url)
    
    # Сканирование
    scan_result = scan_repo(repo_path)
    
    # Очистка
    shutil.rmtree(repo_path, ignore_errors=True)
    print('success')
    return scan_result

def on_message(channel, method_frame, header_frame, body):
    """Обработка входящего сообщения из RabbitMQ"""
    try:
        print(body)
        message = json.loads(body)
        purl = message.get('purl')
        if not purl:
            print("No purl in message")
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return
        
        print(f"Processing PURL: {purl}")
        res = process_purl(purl)
        callback(res, purl)  
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        
    except Exception as e:
        print(f"Error processing message: {e}")
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

def main():
    """Основная функция"""
    credentials = pika.PlainCredentials(username=RABBITMQ_USER, password=RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=5672, credentials=credentials)
    )
    channel = connection.channel()
    
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.basic_consume(
        queue=RABBITMQ_QUEUE,
        on_message_callback=on_message,
        auto_ack=False
    )
    
    print("Waiting for messages. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()

main()