# syntax=docker/dockerfile:1

FROM python:3.11.1-slim

WORKDIR /app

RUN python -m venv flow-env &&\
    . ./flow-env/bin/activate &&\
    python -m pip install pytest-playwright &&\
    python -m playwright install chromium &&\
    python -m playwright install-deps

COPY docker_test_flow_approval.py pytest.ini ./

CMD [ "./flow-env/bin/activate", "&&", "pytest", "docker_test_flow_approval.py"]
