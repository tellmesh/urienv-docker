# urienv-docker OCI image
#
# Build from tellmesh workspace root:
#   docker build -f urienv-docker/Dockerfile /home/tom/github/tellmesh
#
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
COPY urirouter /build/urirouter
COPY uricore /build/uricore
COPY urienv /build/urienv
COPY urienv-docker /build/urienv-docker
COPY urienv-docker/docker/config /app/docker/config
COPY urienv-docker/flows /app/flows
COPY urienv-docker/tests /app/tests

RUN pip install --upgrade pip \
    && pip install -e /build/urirouter -e /build/uricore -e /build/urienv -e /build/urienv-docker \
    && printf '%s\n' '#!/usr/bin/env sh' 'exec python -m uri_control.edge.cli "$@"' > /usr/local/bin/urisys \
    && chmod +x /usr/local/bin/urisys \
    && ln -s /usr/local/bin/urisys /usr/local/bin/urisys-edge

WORKDIR /app
EXPOSE 8790

HEALTHCHECK --interval=10s --timeout=3s --retries=10 CMD python - <<'PY'
import json, urllib.request
with urllib.request.urlopen('http://127.0.0.1:8790/health', timeout=2) as r:
    data=json.loads(r.read().decode())
    assert data.get('ok') is True
PY

CMD ["urisys", "serve", "--packs", "env", "--host", "0.0.0.0", "--port", "8790", "--env-config", "/etc/urisys/env-policy.yaml"]
