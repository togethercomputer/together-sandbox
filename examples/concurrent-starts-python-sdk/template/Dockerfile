FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN echo "Hello from the Together Sandbox!" > /workspace/hello.txt
