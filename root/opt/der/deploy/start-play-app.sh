#!/bin/bash
#usage start-play-app.sh app-name

APP_NAME=$1
PLAY_CONFIG_FILE=/etc/der/play-apps.conf
PORT=`grep -P '^'$APP_NAME' ' $PLAY_CONFIG_FILE | tr -s ' ' | cut -d ' ' -f 2` #getting port from config
EXTRA_ARGS=`grep -P '^'$APP_NAME' ' $PLAY_CONFIG_FILE | tr -s ' ' | cut -d ' ' -f 3-` #getting extra run arguments

if [ "$PORT" == "" ]; then
  echo "failed to find port in the file $PLAY_CONFIG_FILE"
  exit 1
fi

start-stop-daemon --chuid play --start --background --verbose --pidfile /home/play/$APP_NAME/RUNNING_PID --exec /home/play/$APP_NAME/bin/$APP_NAME -- -Dhttp.port=$PORT -Dlogger.file=/etc/der/play-application-logger.xml -Dconfig.file=/home/play/$APP_NAME/application.conf $EXTRA_ARGS