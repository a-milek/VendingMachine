
Authentication is required to manage system service or unit files.
Authenticating as: ,,, (amilek)
Password:
==== AUTHENTICATION COMPLETE ====
==== AUTHENTICATING FOR org.freedesktop.systemd1.reload-daemon ====
Authentication is required to reload the systemd state.
Authenticating as: ,,, (amilek)
Password:
==== AUTHENTICATION COMPLETE ====
chown: changing ownership of '/home/amilek/Documents/Server/WebControls/myenv/include/python3.11': Operation not permitted
chown: changing ownership of '/home/amilek/Documents/Server/WebControls/myenv/include': Operation not permitted
chown: changing ownership of '/home/amilek/Documents/Server/WebControls/myenv/lib/python3.11/site-packages/_distutils_hack/__pycache__/__init__.cpython-311.pyc': Operation not permitted
chown: changing ownership of '/home/amilek/Documents/Server/Websocket/venv/include/python3.11': Operation not permitted
chown: changing ownership of '/home/amilek/Documents/Server/Websocket/venv/include': Operation not permitted
chown: changing ownership of '/home/amilek/Documents/Server/Websocket/venv/lib/python3.11/site-packages/_distutils_hack/__pycache__/__init__.cpython-311.pyc': Operation not permitted
Setup complete.

amilek@raspberrypi:~/Documents/Server $ ./serverscript.sh
Traceback (most recent call last):
  File "/home/amilek/Documents/Server/WebControls/main.py", line 5, in <module>
    from Arduino import Arduino
ModuleNotFoundError: No module named 'Arduino'

amilek@raspberrypi:~/Documents/Server $
  GNU nano 7.2                  /home/amilek/Documents/Server/install.sh
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

