# Use an official Python runtime as a parent image
FROM python:3-slim-buster as builder

RUN curl https://ftp-master.debian.org/keys/release-10.asc | apt-key add - && echo "deb http://deb.debian.org/debian buster non-free" | tee -a /etc/apt/sources.list && apt-get update && apt-get install libttspico-utils

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org --install-option="--prefix=/install" -r /requirements.txt

# IMPORTANT: naming 'as base' is used by cross-platform image publication
FROM python:3-alpine as base

COPY --from=builder /install /usr/local
COPY audio_output /audio_output
WORKDIR /

CMD ["python", "-m", "audio_output.audio"]
