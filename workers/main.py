from scanner.scan import Scanner
from common.download import RepoDownloader
from common.worker import Worker

def main():
    scanner = Scanner()
    downloader = RepoDownloader()
    worker = Worker(scanner, downloader)
    worker.run_work()

if __name__ == '__main__':
    main()
