#!/bin/bash

VNC_PORT=5999
WEB_PORT=6099
DISPLAY_NUM=99

echo "🚀 Démarrage de la stack VNC sur ports isolés..."

pkill -f Xvfb
pkill -f x11vnc
pkill -f websockify
rm -f /tmp/.X99-lock
sleep 1

Xvfb :$DISPLAY_NUM -screen 0 1280x720x24 &
sleep 2

x11vnc -display :$DISPLAY_NUM -forever -shared -nopw -rfbport $VNC_PORT > vnc_server.log 2>&1 &
sleep 2

NOVNC_PATH="/usr/share/novnc"
[ ! -d "$NOVNC_PATH" ] && NOVNC_PATH="/usr/lib/novnc"

websockify --web $NOVNC_PATH $WEB_PORT localhost:$VNC_PORT > websockify.log 2>&1 &

echo "✅ Stack VNC prête sur ports isolés !"
echo "  ▸ VNC : $VNC_PORT"
echo "  ▸ noVNC : $WEB_PORT"
