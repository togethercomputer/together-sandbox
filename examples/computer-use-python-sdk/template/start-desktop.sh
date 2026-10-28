#!/bin/bash
# Starts the desktop and serves it over HTTP on $NOVNC_PORT (default 6080).
# Stays in the foreground (websockify) so the exec running it stays alive.
set -euo pipefail

export DISPLAY=:1
RESOLUTION="${DESKTOP_RESOLUTION:-1280x800}"
NOVNC_PORT="${NOVNC_PORT:-6080}"

mkdir -p "$HOME/.vnc"
x11vnc -storepasswd "$VNC_PASSWORD" "$HOME/.vnc/passwd" >/dev/null

Xvfb "$DISPLAY" -screen 0 "${RESOLUTION}x24" &
until xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; do sleep 0.2; done

dbus-launch --exit-with-session startxfce4 >/tmp/xfce.log 2>&1 &

# VNC listens on localhost only; the outside world reaches it through noVNC.
x11vnc -display "$DISPLAY" -rfbauth "$HOME/.vnc/passwd" -rfbport 5900 \
    -localhost -forever -shared -quiet >/tmp/x11vnc.log 2>&1 &

exec websockify --web /usr/share/novnc "$NOVNC_PORT" localhost:5900
