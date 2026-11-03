FROM node:24-bookworm-slim

# Chromium (Debian's package, not a snap) for OpenClaw's browser tool.
RUN apt-get update && apt-get install -y \
    ca-certificates \
    chromium \
    curl \
    fonts-liberation \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g openclaw@latest

# Sandbox execs run as uid 1000, which is the `node` user here. Install the
# DuckDuckGo web search plugin (no API key needed) into its home directory.
USER node
WORKDIR /home/node
RUN HOME=/home/node openclaw plugins install @openclaw/duckduckgo-plugin

# The image must end as root for the sandbox to start.
USER root
