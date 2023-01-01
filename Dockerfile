# syntax=docker/dockerfile:1

FROM python:3.11.1-slim

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

WORKDIR /app

RUN pip3 install pytest-playwright
RUN playwright install
RUN playwright install-deps

COPY . .

CMD [ "pytest", "docker_test_flow_approval.py"]