FROM ubuntu:24.04

# libatomic1 is needed by the Node.js runtime Hermes downloads. The rest are
# the shared libraries Chromium needs, for Hermes' browser tools.
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    git \
    libatomic1 \
    python3 \
    xz-utils \
    fonts-liberation \
    libasound2t64 \
    libatk-bridge2.0-0t64 \
    libatk1.0-0t64 \
    libatspi2.0-0t64 \
    libcairo2 \
    libcups2t64 \
    libdrm2 \
    libgbm1 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libxkbcommon0 \
    libxrandr2 \
    && rm -rf /var/lib/apt/lists/*

# ubuntu:24.04 ships a `ubuntu` user (uid 1000). Install Hermes into its home
# directory, so the agent can later run as that user instead of root.
USER ubuntu
WORKDIR /home/ubuntu

RUN curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# Download Chromium now, so the browser works as soon as a sandbox starts.
RUN /home/ubuntu/.local/bin/hermes pm install chromium

# The image must end as root for the sandbox to start. start_agent.py runs
# the agent as `ubuntu` by passing the user to each exec explicitly.
USER root
