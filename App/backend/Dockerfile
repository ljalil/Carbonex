FROM ubuntu:22.04 AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    make \
    gzip \
    tar

COPY phreeqc-3.8.6-17100.tar.gz /tmp/phreeqc.tar.gz
WORKDIR /tmp
RUN gunzip phreeqc.tar.gz && tar -xvf phreeqc.tar
WORKDIR /tmp/phreeqc-3.8.6-17100
RUN mkdir Release && \
    cd Release && \
    ../configure --prefix=/usr/local && \
    make -j$(nproc) && \
    make install

FROM python:3.11-slim-bookworm

RUN useradd --create-home appuser

COPY --from=builder /usr/local /usr/local

COPY --chown=appuser:appuser pitzer_mod.dat /usr/local/share/doc/phreeqc/database/

COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

USER appuser
WORKDIR /home/appuser/app

COPY --chown=appuser:appuser . .

EXPOSE 5000

ENV FLASK_ENV=production

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]