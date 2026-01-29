#!/bin/bash

USER="amilek"
USER_HOME="/home/$USER"
TARGET_DIR="$USER_HOME/Documents/Server"

cd ..
mv VendingMachine "$TARGET_DIR"
cd "$TARGET_DIR/WebControls" || exit 1
python3 -m venv venv
source venv/bin/activate
pip install bottle
pip install websockets pyserial
deactivate


cd "$TARGET_DIR/Websocket" || exit 1
python3 -m venv venv
source venv/bin/activate
pip install websockets pyserial
deactivate

cd "$TARGET_DIR/statisticsService" || exit 1
python3 -m venv venv
source venv/bin/activate
pip install bottle
deactivate

mkdir -p "$USER_HOME/.config/autostart"


mv "$TARGET_DIR/machinekiosk.desktop" "$USER_HOME/.config/autostart/" 

mv "$TARGET_DIR/serverbootup.service" /etc/systemd/system/ 
mv "$TARGET_DIR/websocket.service" /etc/systemd/system/ 
mv "$TARGET_DIR/statistics.service" /etc/systemd/system/ 


systemctl daemon-reload
systemctl enable --now serverbootup.service
systemctl enable --now websocket.service
systemctl enable --now statistics.service

curl --silent --location -O https://repos.influxdata.com/influxdata-archive.key
gpg --show-keys --with-fingerprint --with-colons ./influxdata-archive.key 2>&1 \
| grep -q '^fpr:\+24C975CBA61A024EE1B631787C3D57159FC2F927:$' \
&& cat influxdata-archive.key \
| gpg --dearmor \
| sudo tee /etc/apt/keyrings/influxdata-archive.gpg > /dev/null \
&& echo 'deb [signed-by=/etc/apt/keyrings/influxdata-archive.gpg] https://repos.influxdata.com/debian stable main' \
| sudo tee /etc/apt/sources.list.d/influxdata.list
sudo apt-get update && sudo apt-get install telegraf

mv "$TARGET_DIR/telegraf.conf" /etc/telegraf/

systemctl daemon-reload
systemctl restart telegraf

chown -R $USER:$USER "$USER_HOME/.config/autostart"
chown $USER:$USER "$USER_HOME/Documents/Server" -R

echo "Setup complete."

