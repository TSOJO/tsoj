FROM python:3.10-slim

WORKDIR /usr/src/app

RUN apt update && \
    apt install -y make libcap-dev git build-essential && \
    git clone https://github.com/ioi/isolate && \
    make install -C isolate

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

COPY . ./
