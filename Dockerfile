ARG python=python:3.10-slim-bullseye

FROM ${python} AS builder

RUN python -m pip install --upgrade pip && \
    pip install setuptools build wheel

RUN mkdir /src
COPY . /src

WORKDIR /src
RUN python -m build -n

FROM ${python}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-dev \
    libpq-dev && \
    apt-get remove --purge -y && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lob/apt/lists/*

RUN mkdir -p /opt/app/dist

WORKDIR /opt/app

COPY --from=builder /src/dist/*.whl dist
COPY ./scripts scripts

RUN chmod +x ./scripts/*
RUN ./scripts/setup.sh

ENTRYPOINT [ "sh", "./scripts/docker-entrypoint.sh" ]
