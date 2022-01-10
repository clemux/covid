FROM fedora-minimal:latest

WORKDIR /opt/covid

COPY app/ app/
COPY setup.cfg .
COPY pyproject.toml .

COPY website/ website/

RUN microdnf -y update && microdnf -y install python3.10 && microdnf clean all

RUN python3 -m venv venv
RUN venv/bin/pip install -U pip
RUN venv/bin/pip install .

ENV OMP_NUM_THREADS=1

ENTRYPOINT ["/opt/covid/venv/bin/covidmux"]