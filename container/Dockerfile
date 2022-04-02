FROM python:3.9

RUN useradd -ms /bin/bash covid

USER covid

WORKDIR /home/covid

COPY app/ app/
COPY website/ website/
COPY pyproject.toml .
COPY pdm.lock .

# RUN apt update && apt upgrade -y
RUN pip install --user pdm
RUN ~/.local/bin/pdm install

ENTRYPOINT [".local/bin/pdm", "run"]