FROM project-base as semgrep

ARG SEMGREP_APP_TOKEN

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN SEMGREP_APP_TOKEN=$SEMGREP_APP_TOKEN semgrep login

CMD ["python", "main.py"]
