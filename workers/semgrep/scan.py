import subprocess

class Scanner:
    def __init__(self):
        pass

    def scan_repo(target_path):
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
