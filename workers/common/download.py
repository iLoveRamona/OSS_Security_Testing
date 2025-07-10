import shutil
import zipfile
import tarfile
import subprocess
import os
from pathlib import Path

class RepoDownloader:
    def extract_tar_gz(self, archive_path, dest_dir):
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=dest_dir)

    def extract_zip(self, archive_path, dest_dir):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(dest_dir)

    def download_repo(self, repo_url):
        if not repo_url:
            raise ValueError("Repository URL not provided")
        ext = 'tar.gz' if 'tar.gz' in repo_url else 'zip'

        archive_path = Path(f"./target.{ext}")
        extract_dir = Path("./extracted")

        shutil.rmtree(extract_dir, ignore_errors=True)
        extract_dir.mkdir()

        curl_cmd = f"curl -s -L -o {archive_path} {repo_url}"
        curl_result = subprocess.run(
            curl_cmd, shell=True, capture_output=True, text=True
        )

        if curl_result.returncode != 0:
            raise RuntimeError(f"Curl error: {curl_result.stderr}")

        if ext == 'tar.gz':
            self.extract_tar_gz(archive_path, extract_dir)
        else:
            self.extract_zip(archive_path, extract_dir)
        os.remove(archive_path)

        self.repo_path = str(extract_dir)
        return self.repo_path

    def remove_dir(self):
        shutil.rmtree(self.repo_path, ignore_errors=True)
