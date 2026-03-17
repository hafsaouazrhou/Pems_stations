# ─────────────────────────────────────────────────────────────────────────────
# PeMSD7 Traffic Stations – Single-container Dockerfile (v4)
#  Base : mongo:7 (Debian Bookworm, MongoDB natif et complet)
#  Python installé via deadsnakes PPA → pas de conflit pip
# ─────────────────────────────────────────────────────────────────────────────
FROM mongo:7

# ── Python 3.11 + pip + supervisor ───────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        supervisor \
        procps \
    && rm -rf /var/lib/apt/lists/*

# ── Répertoires ───────────────────────────────────────────────────────────────
RUN mkdir -p /data/db /var/log/supervisor

# ── Virtualenv Python (évite tout conflit système) ────────────────────────────
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# ── Dépendances Python ────────────────────────────────────────────────────────
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Code applicatif ───────────────────────────────────────────────────────────
COPY app.py       .
COPY templates/   templates/
COPY data/        data/

# ── Supervisord ───────────────────────────────────────────────────────────────
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 5000

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
