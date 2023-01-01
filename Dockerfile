# syntax=docker/dockerfile:1

FROM python:latest

WORKDIR /app

RUN pip3 install pytest-playwright
RUN playwright install

COPY . .

CMD [ "pytest", "docker_test_flow_approval.py"]