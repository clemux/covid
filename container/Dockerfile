FROM fedora:latest

WORKDIR /opt/covid

COPY app/ app/
COPY setup.cfg .
COPY pyproject.toml .

COPY website/ website/

RUN dnf -y update && dnf -y install hugo python3.10 && dnf clean all

RUN python3 -m venv venv
RUN venv/bin/pip install -U pip
RUN venv/bin/pip install .

ENTRYPOINT ["/opt/covid/venv/bin/covidmux"]