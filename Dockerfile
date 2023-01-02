# syntax=docker/dockerfile:1

FROM python:3.11.1-slim

WORKDIR /app

RUN pip3 install pytest-playwright &&\
    playwright install &&\
    playwright install-deps

COPY . .

CMD [ "pytest", "docker_test_flow_approval.py"]