ARG BUILD_FROM=ghcr.io/home-assistant/base:3.24-2026.10.1

# renovate: datasource=repology depName=alpine_3_24/git
ARG GIT_VERSION=2.54.0-r0
# renovate: datasource=repology depName=alpine_3_24/python3
ARG PYTHON_VERSION=3.14.8-r0
# renovate: datasource=repology depName=alpine_3_24/py3-yaml
ARG PY3_YAML_VERSION=6.0.3-r2

FROM ${BUILD_FROM}

# The exporter is plain Python (standard library and PyYAML) and git; nothing else is needed.
ARG GIT_VERSION
ARG PYTHON_VERSION
ARG PY3_YAML_VERSION
RUN apk add --no-cache \
    git=${GIT_VERSION} \
    python3=${PYTHON_VERSION} \
    py3-yaml=${PY3_YAML_VERSION}

COPY rootfs/ /
COPY LICENSE THIRD_PARTY_NOTICES.md /usr/share/licenses/git-exporter/

# Git does not keep the executable bit when files are uploaded through the GitHub API.
RUN find /etc/s6-overlay/s6-rc.d -type f \( -name run -o -name finish \) -exec chmod a+x {} +

ARG BUILD_VERSION=2.0.0-beta.1
ARG BUILD_ARCH=amd64
RUN mkdir -p /etc/git-exporter && echo "${BUILD_VERSION}" >/etc/git-exporter/version
LABEL io.hass.version="${BUILD_VERSION}" \
    io.hass.type="addon" \
    io.hass.arch="${BUILD_ARCH}" \
    org.opencontainers.image.source="https://github.com/seb5594/Home-Assistant-git-exporter-Addon"

ENV PYTHONPATH=/opt/git-exporter \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

HEALTHCHECK --interval=5m --timeout=10s --start-period=1m --retries=3 \
    CMD ["python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8099/api/log', timeout=5)"]
