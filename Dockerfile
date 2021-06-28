FROM python:3.6

RUN apt-get update && apt-get install -y wget virtualenv


EXPOSE 8003

RUN mkdir -p /app
WORKDIR /app

VOLUME /reports

ADD . /app/

RUN pip install -r requirements.txt


