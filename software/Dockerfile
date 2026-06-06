# Container image for the Music Box web faceplate (Flask + SoCo).
# Build context is this software/ directory. Served by gunicorn.
#
# Run needs host networking so SoCo's SSDP discovery can see the Sonos
# speakers on the LAN — see infra/musicbox in the skjoldjasper repo.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MUSICBOX_PORT=8080

WORKDIR /app

# Deps first for layer caching. gunicorn is production-only, so it's added
# here rather than in requirements.txt (which stays the minimal dev set).
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

EXPOSE 8080

# One worker on purpose: the MusicBox state (armed rooms, playing flag, the
# card on the spot) lives in process memory, so multiple workers would serve
# inconsistent UI state. The long timeout absorbs the ~10s Sonos SSDP
# discovery that runs once at import.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${MUSICBOX_PORT:-8080} --workers 1 --timeout 120 --access-logfile - web.server:app"]
