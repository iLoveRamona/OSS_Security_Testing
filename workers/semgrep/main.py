from scan import Scanner
from common.download import RepoDownloader
from common.worker import Worker
import subprocess
import config
import sys

def login_to_semgrep():
    result = subprocess.run(
        'semgrep login',
        shell=True,
        env={'SEMGREP_APP_TOKEN': config.SEMGREP_APP_TOKEN}
    )
    if result.returncode != 0:
        print('SEMGREP_APP_TOKEN not provided', file=sys.stderr)

def main():
    login_to_semgrep()

    scanner = Scanner()
    downloader = RepoDownloader()
    worker = Worker(downloader, scanner)
    worker.run_work()

if __name__ == '__main__':
    main()
