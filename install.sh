#!/bin/bash

# Ustaw użytkownika i ścieżki
USER="amilek"
USER_HOME="/home/$USER"
TARGET_DIR="$USER_HOME/Documents/Server"

cd "$TARGET_DIR/WebControls" || exit 1
python3 -m venv myenv
source myenv/bin/activate
pip install bottle
deactivate


cd "$TARGET_DIR/Websocket" || exit 1
python3 -m venv venv
source venv/bin/activate
pip install websockets pyserial
deactivate

mkdir -p "$USER_HOME/.config/autostart"


mv "$TARGET_DIR/machinekiosk.desktop" "$USER_HOME/.config/autostart/" || echo "Warning: machinekio>

mv "$TARGET_DIR/serverbootup.service" /etc/systemd/system/ || echo "Warning: serverbootup.service >
mv "$TARGET_DIR/websocket.service" /etc/systemd/system/ || echo "Warning: websocket.service not fo>


systemctl daemon-reload
systemctl enable serverbootup.service
systemctl enable websocket.service


chown -R $USER:$USER "$USER_HOME/.config/autostart"
chown $USER:$USER "$USER_HOME/Documents/Server" -R

echo "Setup complete."

