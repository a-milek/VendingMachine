#!/bin/bash

USER="amilek"
USER_HOME="/home/$USER"
TARGET_DIR="$USER_HOME/Documents/Server"

cd ..
mv VendingMachine "$TARGET_DIR"
cd "$TARGET_DIR/WebControls" || exit 1
python3 -m venv myenv
source myenv/bin/activate
pip install bottle
pip install websockets pyserial
deactivate


cd "$TARGET_DIR/Websocket" || exit 1
python3 -m venv venv
source venv/bin/activate
pip install websockets pyserial
deactivate

mkdir -p "$USER_HOME/.config/autostart"


mv "$TARGET_DIR/machinekiosk.desktop" "$USER_HOME/.config/autostart/" 

mv "$TARGET_DIR/serverbootup.service" /etc/systemd/system/ 
mv "$TARGET_DIR/websocket.service" /etc/systemd/system/ 


systemctl daemon-reload
systemctl enable serverbootup.service
systemctl enable websocket.service


chown -R $USER:$USER "$USER_HOME/.config/autostart"
chown $USER:$USER "$USER_HOME/Documents/Server" -R

echo "Setup complete."

