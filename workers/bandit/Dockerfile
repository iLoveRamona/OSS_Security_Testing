FROM worker-base as bandit

WORKDIR /app

COPY . ./bandit

RUN pip install --no-cache-dir -r ./bandit/requirements.txt

CMD ["python", "main.py"]
