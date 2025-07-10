FROM worker-base as semgrep

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . ./scanner

CMD ["python", "main.py"]
