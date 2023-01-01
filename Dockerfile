# syntax=docker/dockerfile:1

FROM ubuntu:latest

WORKDIR /app

RUN pip install pytest-playwright
RUN playwright install

COPY . .

CMD [ "pytest", "docker_test_flow_approval.py"]