FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

RUN apt update && \
    apt install -y make libcap-dev && \
    git clone https://github.com/ioi/isolate && \
    make install -C isolate

COPY . ./
