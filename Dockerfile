FROM node:22-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium python3 ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @testmuai/kane-cli@0.10.9
RUN useradd -m -u 10001 forge
WORKDIR /app
COPY --chown=forge:forge skillforge/ /app/skillforge/
COPY --chown=forge:forge forge.py /app/
COPY --chown=forge:forge examples/ /app/examples/
COPY --chown=forge:forge demo/ /app/demo/
USER forge
ENV CHROME_BIN=/usr/bin/chromium
ENV SKILLFORGE_HOME=/home/forge/registry
ENTRYPOINT ["python3", "/app/forge.py"]
