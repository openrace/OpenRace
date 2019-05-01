# Use an official Python runtime as a parent image
FROM python:3-slim as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org --install-option="--prefix=/install" -r /requirements.txt

FROM python:3-alpine

COPY --from=builder /install /usr/local
COPY race_core /race_core
WORKDIR /

CMD ["python", "-m", "race_core.core", "--device", "/dev/racetracker"]
