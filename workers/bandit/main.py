from scan import Scanner
from common.download import RepoDownloader
from common.worker import Worker

def main():
    scanner = Scanner()
    downloader = RepoDownloader()
    worker = Worker(downloader, scanner)
    worker.run_work()

if __name__ == '__main__':
    main()
