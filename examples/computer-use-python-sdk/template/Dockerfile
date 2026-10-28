FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

# XFCE desktop on a virtual X display (Xvfb), exported over VNC (x11vnc) and
# served to the browser by noVNC (websockify + the noVNC web client).
RUN apt-get update && apt-get install -y --no-install-recommends \
    xfce4 \
    xfce4-terminal \
    dbus-x11 \
    xvfb \
    x11-utils \
    x11vnc \
    novnc \
    websockify \
    firefox-esr \
    fonts-dejavu \
    ca-certificates \
    curl \
    git \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# start_desktop.py runs the desktop as uid 1000, so give it a real user and home.
RUN useradd -m -u 1000 -s /bin/bash user \
    && echo "user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/user \
    && mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix

# Opening the port's root URL lands straight in a connected, auto-resizing session.
RUN echo '<meta http-equiv="refresh" content="0; url=vnc.html?autoconnect=1&resize=remote">' \
    > /usr/share/novnc/index.html

COPY start-desktop.sh /usr/local/bin/start-desktop.sh
RUN chmod +x /usr/local/bin/start-desktop.sh

WORKDIR /home/user
