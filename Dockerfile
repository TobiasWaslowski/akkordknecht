FROM python:3.8

COPY requirements.txt .
COPY config.yml .

RUN pip install -r requirements.txt

COPY src/ ./src

CMD [ "python", "src/main.py"]
