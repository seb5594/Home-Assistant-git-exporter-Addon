ARG BUILD_FROM=ghcr.io/home-assistant/base:3.24-2026.08.0

# renovate: datasource=repology depName=alpine_3_24/git
ARG GIT_VERSION=2.54.0-r0
# renovate: datasource=repology depName=alpine_3_22/git
ARG GIT_VERSION_LEGACY=2.49.1-r0
# renovate: datasource=repology depName=alpine_3_24/make
ARG MAKE_VERSION=4.4.1-r4
# renovate: datasource=repology depName=alpine_3_22/make
ARG MAKE_VERSION_LEGACY=4.4.1-r3
# renovate: datasource=repology depName=alpine_3_24/rsync
ARG RSYNC_VERSION=3.5.0-r0
# renovate: datasource=repology depName=alpine_3_22/rsync
ARG RSYNC_VERSION_LEGACY=3.5.0-r0
# renovate: datasource=repology depName=alpine_3_24/grep
ARG GREP_VERSION=3.12-r0
# renovate: datasource=repology depName=alpine_3_22/grep
ARG GREP_VERSION_LEGACY=3.12-r0
# renovate: datasource=repology depName=alpine_3_24/sed
ARG SED_VERSION=4.9-r2
# renovate: datasource=repology depName=alpine_3_22/sed
ARG SED_VERSION_LEGACY=4.9-r2
# renovate: datasource=repology depName=alpine_3_24/python3
ARG PYTHON_VERSION=3.14.8-r0
# renovate: datasource=repology depName=alpine_3_22/python3
ARG PYTHON_VERSION_LEGACY=3.12.15-r0
# renovate: datasource=repology depName=alpine_3_24/py3-yaml
ARG PY3_YAML_VERSION=6.0.3-r2
# renovate: datasource=repology depName=alpine_3_22/py3-yaml
ARG PY3_YAML_VERSION_LEGACY=6.0.2-r0
# renovate: datasource=repology depName=alpine_3_24/findutils
ARG FINDUTILS_VERSION=4.10.0-r1
# renovate: datasource=repology depName=alpine_3_22/findutils
ARG FINDUTILS_VERSION_LEGACY=4.10.0-r0

FROM ${BUILD_FROM} AS build

ARG GIT_VERSION
ARG MAKE_VERSION
RUN apk add --no-cache git=${GIT_VERSION} make=${MAKE_VERSION}

# renovate: datasource=github-tags depName=awslabs/git-secrets
ENV GIT_SECRET_VERSION=1.3.0
RUN git config --global advice.detachedHead false && \
    git clone --depth 1 https://github.com/awslabs/git-secrets.git -b ${GIT_SECRET_VERSION} /git-secrets && \
    make -C /git-secrets install

FROM ${BUILD_FROM} AS running

ARG GIT_VERSION
ARG RSYNC_VERSION
ARG GREP_VERSION
ARG SED_VERSION
ARG PYTHON_VERSION
ARG PY3_YAML_VERSION
ARG FINDUTILS_VERSION
RUN apk add --no-cache \
    git=${GIT_VERSION} \
    rsync=${RSYNC_VERSION} \
    grep=${GREP_VERSION} \
    sed=${SED_VERSION} \
    python3=${PYTHON_VERSION} \
    py3-yaml=${PY3_YAML_VERSION} \
    findutils=${FINDUTILS_VERSION}

ARG BUILD_VERSION=1.19.0
ARG BUILD_ARCH=amd64
LABEL io.hass.version="${BUILD_VERSION}" \
    io.hass.type="addon" \
    io.hass.arch="${BUILD_ARCH}" \
    org.opencontainers.image.source="https://github.com/seb5594/Home-Assistant-git-exporter-Addon"

COPY --from=build /usr/local/bin/git-secrets /usr/local/bin/git-secrets
COPY root /
COPY entrypoint.sh /
RUN chmod a+x /run.sh /entrypoint.sh /utils/*
ENTRYPOINT [ "/bin/bash", "/entrypoint.sh" ]
CMD [ "/run.sh" ]
