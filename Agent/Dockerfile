# ── Stage 1: build PHREEQC from source ──────────────────────────────────────
FROM ubuntu:22.04 AS phreeqc-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential make gzip tar \
    && rm -rf /var/lib/apt/lists/*

COPY docker/phreeqc-3.8.6-17100.tar.gz /tmp/phreeqc.tar.gz
WORKDIR /tmp
RUN tar -xzf phreeqc.tar.gz
WORKDIR /tmp/phreeqc-3.8.6-17100
RUN mkdir Release && \
    cd Release && \
    ../configure --prefix=/usr/local && \
    make -j$(nproc) && \
    make install

# ── Stage 2: runtime ────────────────────────────────────────────────────────
FROM python:3.13.13-trixie

RUN useradd --create-home appuser

# Copy PHREEQC binary + default databases from build stage
COPY --from=phreeqc-builder /usr/local /usr/local

# pitzer_mod.dat is a custom database not shipped with the default PHREEQC install
COPY --chown=appuser:appuser docker/pitzer_mod.dat \
    /usr/local/share/doc/phreeqc/database/pitzer_mod.dat

# Install Python dependencies before copying source so this layer is cached
COPY --chown=appuser:appuser requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

USER appuser
WORKDIR /home/appuser/app

# Copy app source — shadowed by the volume mount during local development
COPY --chown=appuser:appuser . .

EXPOSE 8000

CMD ["chainlit", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
