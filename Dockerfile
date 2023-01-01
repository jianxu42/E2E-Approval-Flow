# syntax=docker/dockerfile:1

FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

WORKDIR /app

RUN pip3 install pytest-playwright
RUN playwright install

COPY . .

CMD [ "pytest", "docker_test_flow_approval.py"]