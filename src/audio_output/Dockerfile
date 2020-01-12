# Use an official Python runtime as a parent image
FROM python:3-buster

RUN wget -q https://ftp-master.debian.org/keys/release-10.asc -O- | apt-key add - && echo "deb http://deb.debian.org/debian buster non-free" | tee -a /etc/apt/sources.list && apt update && apt -y install libttspico-utils alsa-utils

WORKDIR /

COPY requirements.txt /requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org --install-option="--prefix=/install" -r /requirements.txt

COPY audio_output /audio_output

CMD ["python", "-m", "audio_output.audio"]
