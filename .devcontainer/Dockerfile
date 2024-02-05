FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y xz-utils

RUN apt-get update && \
    apt-get install -y \
    xz-utils \
    libglib2.0-0

COPY requirements.txt requirements.txt

# Install requirements
RUN python3 -m pip install -r requirements.txt
RUN python3 -m pip install torch

RUN python3 -m pip install ipykernel && \
    python3 -m ipykernel install --user

WORKDIR /workspace