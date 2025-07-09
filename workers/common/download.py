import shutil
import zipfile
import subprocess
from pathlib import Path

class RepoDownloader:
    def download_repo(self, repo_url):
        if not repo_url:
            raise ValueError("Repository URL not provided")

        zip_path = Path("/tmp/target.zip")
        extract_dir = Path("/tmp/extracted")

        shutil.rmtree(extract_dir, ignore_errors=True)
        extract_dir.mkdir()

        curl_cmd = f"curl -s -L -o {zip_path} {repo_url}"
        curl_result = subprocess.run(
            curl_cmd, shell=True, capture_output=True, text=True
        )

        if curl_result.returncode != 0:
            raise RuntimeError(f"Curl error: {curl_result.stderr}")

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        self.repo_path = str(extract_dir)
        return self.repo_path

    def remove_dir(self):
        shutil.rmtree(self.repo_path, ignore_errors=True)
