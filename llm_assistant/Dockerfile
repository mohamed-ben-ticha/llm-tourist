FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY app.py .
COPY .env .

EXPOSE 5000

CMD [ "python3", "app.py"]