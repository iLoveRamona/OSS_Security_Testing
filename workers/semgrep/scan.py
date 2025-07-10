import subprocess
from scanner import config
import sys

class Scanner:
    def __init__(self):
        print(f'semgrep token: {config.SEMGREP_APP_TOKEN}')
        result = subprocess.run(
            f'SEMGREP_APP_TOKEN={config.SEMGREP_APP_TOKEN} semgrep login',
            shell=True
        )
        if result.returncode != 0:
            print('SEMGREP_APP_TOKEN not provided', file=sys.stderr)

    def scan_repo(self, target_path):
        result = subprocess.run(
            f"semgrep --config=auto --json-output=/tmp/semgrep_result.json {target_path}",
            shell=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Semgrep failed: {result.stderr}")

        return {
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        }
