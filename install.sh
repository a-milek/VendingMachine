#!/bin/bash

# Ustaw użytkownika i ścieżki
USER="amilek"
USER_HOME="/home/$USER"
TARGET_DIR="$USER_HOME/Documents/Server"


mkdir -p "$TARGET_DIR"

echo "Repository cloned to $TARGET_DIR"

cd "$TARGET_DIR/WebControls" || exit 1
python3 -m venv myenv
source myenv/bin/activate
deactivate


cd "$TARGET_DIR/Websocket" || exit 1
python3 -m venv venv
source venv/bin/activate
pip install websockets pyserial
deactivate

mkdir -p "$USER_HOME/.config/autostart"


mv "$TARGET_DIR/machinekiosk.desktop" "$USER_HOME/.config/autostart/" || echo "Warning: machinekiosk.desktop not found"

mv "$TARGET_DIR/serverbootup.service" /etc/systemd/system/ || echo "Warning: serverbootup.service not found"
mv "$TARGET_DIR/websocket.service" /etc/systemd/system/ || echo "Warning: websocket.service not found"


systemctl daemon-reload
systemctl enable serverbootup.service
systemctl enable websocket.service
systemctl start serverbootup.service
systemctl start websocket.service


systemctl status serverbootup.service
systemctl status websocket.service

chown -R $USER:$USER "$USER_HOME/.config/autostart"
chown $USER:$USER "$USER_HOME/Documents/Server" -R

echo "Setup complete."
