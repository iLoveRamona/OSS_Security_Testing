import pika
import json
import requests
from common.find_url import get_repo_url
from common import config
from scanner import config as scanner_config

class Worker:
    def __init__(self, scanner, downloader):
        self.scanner = scanner
        self.downloader = downloader

    def callback(self, report, purl):
        payload = {
        'report': report,
        'passwd': config.WEB_SECRET,
        'purl': purl,
        'user': config.WEB_USER
    }
        try:
            response = requests.post(f"{config.WEB_URL}/api/v1/report", json=payload)
            response.raise_for_status()
            print(f"Report for {purl} sent successfully")
        except requests.RequestException as e:
            print(f"Failed to send report for {purl}: {e}")

    def process_purl(self, purl_str):
        repo_url = get_repo_url(purl_str)
        if not repo_url:
            raise ValueError("Could not determine repository URL")

        repo_path = self.downloader.download_repo(repo_url)
        scan_result = self.scanner.scan_repo(repo_path)
        self.callback(scan_result['output'], purl_str)
        self.downloader.remove_dir()
        print('success')
        
        return scan_result

    def on_message(self, channel, method_frame, header_frame, body):
        purl = None
        try:
            print(body)
            message = json.loads(body)
            purl = message.get('purl')
            if not purl:
                print("No purl in message")
                raise Exception("No purl in message")

            print(f"Processing PURL: {purl}")
            self.process_purl(purl)
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        except Exception as e:
            print(f"Error processing message: {e}")
            self.callback(None, purl)
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def run_work(self):
        credentials = pika.PlainCredentials(username=config.RABBITMQ_USER, password=config.RABBITMQ_PASS)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=config.RABBITMQ_HOST, port=5672, credentials=credentials)
        )
        channel = connection.channel()

        channel.queue_declare(queue=scanner_config.RABBITMQ_QUEUE, durable=True)
        channel.basic_consume(
            queue=scanner_config.RABBITMQ_QUEUE,
            on_message_callback=self.on_message,
            auto_ack=False
        )

        print("Waiting for messages. To exit press CTRL+C")
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
        connection.close()
