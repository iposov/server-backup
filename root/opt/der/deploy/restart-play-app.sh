#!/bin/bash
APP_NAME=$1
/opt/der/deploy/stop-play-app.sh $APP_NAME
/opt/der/deploy/start-play-app.sh $APP_NAME
