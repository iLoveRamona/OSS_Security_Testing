def scan_repo(target_path):
    """Сканирование репозитория с помощью Bandit"""
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