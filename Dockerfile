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

COPY --from=builder /src/dist/*.whl /opt/app/dist
COPY ./scripts/*.sh /opt/app/scripts

RUN chmod +x /opt/app/scripts/*
RUN /opt/app/scripts/setup.sh

ENTRYPOINT [ "./scripts/entrypoint.sh" ]
