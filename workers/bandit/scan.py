import subprocess
import ast

class Scanner:
    def __init__(self):
        pass

    def scan_repo(self, target_path):
        result = subprocess.run(
            f"bandit -q -r {target_path} -f json",
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode not in [0, 1]:
            raise RuntimeError(f"Bandit failed: {result.stderr}")
        package = result.stdout
        print(package)
        package = ast.literal_eval(package)
        severities_package = package['metrics']['_totals']

        data = {
            "language": "python",
            "scanner": "bandit",
            "high": severities_package["SEVERITY.HIGH"],
            "medium": severities_package["SEVERITY.MEDIUM"],
            "low": severities_package["SEVERITY.LOW"]
        }
        return {
            "output": data,
            "error": result.stderr,
            "return_code": result.returncode
        }
