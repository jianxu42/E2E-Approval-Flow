# syntax=docker/dockerfile:1

FROM ubuntu:latest

RUN apt-get update && apt-get install -y software-properties-common gcc && \
    add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.11 python3-distutils python3-pip python3-apt

WORKDIR /app

RUN pip3 install pytest-playwright
RUN playwright install

COPY . .

CMD [ "pytest", "docker_test_flow_approval.py"]