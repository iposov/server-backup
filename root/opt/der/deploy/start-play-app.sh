#!/bin/bash
#usage start-play-app.sh app-name

APP_NAME=$1
PLAY_CONFIG_FILE=/etc/der/play-apps.conf
PORT=`awk '$1 == "'$APP_NAME'" {print $2}' $PLAY_CONFIG_FILE` #getting port from config

if [ "$PORT" == "" ]; then
  echo "failed to find port in the file $PLAY_CONFIG_FILE"
  exit 1
fi

start-stop-daemon --chuid play --start --background --verbose --pidfile /home/play/$APP_NAME/RUNNING_PID --exec /home/play/$1/bin/$1 -- -Dhttp.port=$PORT -Dlogger.file=/etc/der/application-logger.xml -Dconfig.file=/home/play/$APP_NAME/application.conf

