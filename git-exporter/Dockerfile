ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.22-2025.11.1
FROM ${BUILD_FROM} AS build

# Previous Alpine 3.16 pins: git=2.36.6-r0 and make=4.3-r0.
RUN apk add --no-cache git make

ENV GIT_SECRET_VERSION=1.3.0
# hadolint ignore=DL3003
RUN git config --global advice.detachedHead false && \
    git clone --depth 1 https://github.com/awslabs/git-secrets.git -b ${GIT_SECRET_VERSION} /git-secrets && \
    cd /git-secrets && make install

FROM ${BUILD_FROM} AS running

# Replaces obsolete Alpine 3.16 packages and the pip/PyYAML build step.
# Previous versions: git=2.36.6-r0, rsync=3.2.7-r0, grep=3.7-r0,
# sed=4.8-r0, python3=3.10.14-r1, py3-pip=22.1.1-r0, findutils=4.9.0-r0.
# Previous pip dependencies: PyYAML==5.3.1 dotty-dict==1.3.1.
RUN apk add --no-cache git rsync grep sed python3 py3-yaml findutils

ARG BUILD_VERSION=1.18.0
ARG BUILD_ARCH=amd64
LABEL io.hass.version="${BUILD_VERSION}" \
    io.hass.type="addon" \
    io.hass.arch="${BUILD_ARCH}" \
    org.opencontainers.image.source="https://github.com/seb5594/Home-Assistant-git-exporter-Addon"

COPY --from=build /usr/local/bin/git-secrets /usr/local/bin/git-secrets
COPY root /
COPY entrypoint.sh /
RUN chmod a+x /run.sh /entrypoint.sh /utils/*
# Previous direct entrypoint: ENTRYPOINT [ "/run.sh" ]
ENTRYPOINT [ "/bin/bash", "/entrypoint.sh" ]
CMD [ "/run.sh" ]
