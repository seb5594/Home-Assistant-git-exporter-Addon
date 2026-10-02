# Official Home Assistant base image, pinned to a published release.
ARG BUILD_FROM=ghcr.io/home-assistant/base:3.24-2026.08.0

FROM ${BUILD_FROM} AS build

RUN apk add --no-cache \
    # renovate: datasource=repology depName=alpine_3_24/git
    git=2.54.0-r0 \
    # renovate: datasource=repology depName=alpine_3_24/make
    make=4.4.1-r4

# renovate: datasource=github-tags depName=awslabs/git-secrets
ENV GIT_SECRET_VERSION=1.3.0
RUN git config --global advice.detachedHead false && \
    git clone --depth 1 https://github.com/awslabs/git-secrets.git -b ${GIT_SECRET_VERSION} /git-secrets && \
    make -C /git-secrets install

FROM ${BUILD_FROM} AS running

RUN apk add --no-cache \
    # renovate: datasource=repology depName=alpine_3_24/git
    git=2.54.0-r0 \
    # renovate: datasource=repology depName=alpine_3_24/rsync
    rsync=3.5.0-r0 \
    # renovate: datasource=repology depName=alpine_3_24/grep
    grep=3.12-r0 \
    # renovate: datasource=repology depName=alpine_3_24/sed
    sed=4.9-r2 \
    # renovate: datasource=repology depName=alpine_3_24/python3
    python3=3.14.8-r0 \
    # renovate: datasource=repology depName=alpine_3_24/py3-yaml
    py3-yaml=6.0.3-r2 \
    # renovate: datasource=repology depName=alpine_3_24/findutils
    findutils=4.10.0-r1

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
