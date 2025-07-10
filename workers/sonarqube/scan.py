import subprocess
from scanner import config
import string
import sys
import requests
import time
import re
import secrets
import json


class Scanner:
    def __init__(self, language="python"):
        self.language = language
        self.token = config.SONAR_TOKEN
        self.host = config.SONAR_HOST_URL


    def generate_project_key(self, length = 16):
        alphabet = string.ascii_lowercase
        self.project_key = "".join(secrets.choice(alphabet) for _ in range(length))


    def get_command(self, target_path):
        self.generate_project_key()

        return [
            "sonar-scanner",
            f"-Dsonar.projectKey={self.project_key}",
            f"-Dsonar.host.url={self.host}",
            f"-Dsonar.login={self.token}",
            f"-Dsonar.sources={target_path}"
        ]


    def scan_repo(self, target_path):
        result = subprocess.run(
            self.get_command(target_path),
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Sonarqube failed: {result.stderr}")

        match = re.search(r"ce/task\?id=([a-zA-Z0-9_-]+)", result.stdout)
        if not match:
            print("ERROR: Could not find SonarQube Task ID in the scanner output.")
            sys.exit(1)

        task_id = match.group(1)
        print(f"Task id: {task_id}")
        self.wait_for_task_completion(task_id)

        result = self.fetch_scan_result()
        return {
            "output": self.get_results_json(result),
            "error": result.stderr,
            "return_code": result.returncode
        }

    def get_results_json(self, output):
        data = {
            "language": self.language,
            "scanner": "sonarqube"
        }

        vulners_count = {
            "BLOCKER": 0,
            "CRITICAL": 0,
            "MAJOR": 0,
            "BLOCKER": 0,
            "CRITICAL": 0
        }

        results = json.loads(output)["issues"]
        for result in results:
            vulners_count[result["severity"]] += 1

        data["low"] = vulners_count["BLOCKER"] + vulners_count["CRITICAL"]
        data["medium"] = vulners_count["MAJOR"]
        data["high"] = vulners_count["MINOR"] + vulners_count["INFO"]

        return data


    def fetch_scan_result(self):
        api_url = f"{self.host}/api/issues/search"
        params = {"componentKeys": self.project_key, "ps": 500, "impactSoftwareQualities": "SECURITY"}
        try:
            response = requests.get(api_url, params=params, auth=(self.token, ""))
            response.raise_for_status()
            data = response.json()
            return data.dumps()
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to connect to SonarQube API: {e}")
            sys.exit(1)


    def wait_for_task_completion(self, task_id, timeout_sec: int = 300):
        start_time = time.time()
        api_url = f"{self.host}/api/ce/task"
        params = {"id": task_id}

        while True:
            if time.time() - start_time > timeout_sec:
                print(f"ERROR: Timeout of {timeout_sec} seconds reached while waiting for analysis.")
                sys.exit(1)

            try:
                response = requests.get(api_url, params=params, auth=(self.token, ""))
                response.raise_for_status()
                task_status = response.json()["task"]["status"]

                print(f"Current analysis status: {task_status}")

                if task_status == "SUCCESS":
                    print("Analysis completed successfully.")
                    return # Exit the loop and function
                elif task_status in ["FAILED", "CANCELED"]:
                    print(f"ERROR: Analysis task failed with status: {task_status}")
                    sys.exit(1)
                # If PENDING or IN_PROGRESS, continue polling

            except requests.exceptions.RequestException as e:
                print(f"Warning: Could not check task status (will retry): {e}")

            time.sleep(10)
