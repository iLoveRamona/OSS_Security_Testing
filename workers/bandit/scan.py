import subprocess

class Scanner:
    def __init__(self):
        pass

    def scan_repo(self, target_path):
        result = subprocess.run(
            f"bandit -r {target_path} -f json",
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode not in [0, 1]:
            raise RuntimeError(f"Bandit failed: {result.stderr}")

        return {
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        }
