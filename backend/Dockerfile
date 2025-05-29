FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3 \
    python3-pip \
    python3-venv

COPY phreeqc-3.8.6-17100.tar.gz /tmp/phreeqc.tar.gz

WORKDIR /tmp

RUN gunzip phreeqc.tar.gz && \
    tar -xvf phreeqc.tar

WORKDIR /tmp/phreeqc-3.8.6-17100

RUN mkdir Release && \
    cd Release && \
    ../configure --prefix=/usr/local && \
    make -j$(nproc) && \
    make install

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --break-system-packages -r requirements.txt

# Copy application code (will be overridden by volume in development)
COPY . .

EXPOSE 5000

ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

CMD ["python3", "app.py"]