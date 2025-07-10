import subprocess
import config
import sys
import json

class Scanner:
    def __init__(self, language="python"):
        self.language = language
        print(f'semgrep token: {config.SEMGREP_APP_TOKEN}')
        result = subprocess.run(
            f'SEMGREP_APP_TOKEN={config.SEMGREP_APP_TOKEN} semgrep login',
            shell=True
        )
        if result.returncode != 0:
            print('SEMGREP_APP_TOKEN not provided', file=sys.stderr)

    def scan_repo(self, target_path):
        result = subprocess.run(
            f"semgrep --config=auto --json -q {target_path}",
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Semgrep failed: {result.stderr}")

        print(result.stdout)
        return {
            "output": self.get_results_json(result.stdout),
            "error": result.stderr,
            "return_code": result.returncode
        }

    def get_results_json(self, output):
        data = {
            "language": self.language,
            "scanner": "semgrep"
        }

        vulners_count = {
            "INFO": 0,
            "WARNING": 0,
            "ERROR": 0
        }

        results = json.loads(output)["results"]
        for result in results:
            if result["extra"]["metadata"]["category"] == "security":
                vulners_count[result["extra"]["severity"]] += 1

        data["low"] = vulners_count["INFO"]
        data["medium"] = vulners_count["WARNING"]
        data["high"] = vulners_count["ERROR"]

        return data
