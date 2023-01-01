# syntax=docker/dockerfile:1

FROM python:3.11.1-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install pytest-playwright
RUN playwright install

COPY . .

CMD [ "pytest"]