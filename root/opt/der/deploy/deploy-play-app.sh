#!/bin/bash
#usage deploy-play-app app-name

APP_NAME=$1
DIST_FOLDER=/home/deploy/tmp/$APP_NAME

#read distribution file name
DIST_FILE_NAME_HINT=$DIST_FOLDER/.dist.name
DIST_FILE_NAME=`cat $DIST_FILE_NAME_HINT`

DIST_FILE=$DIST_FOLDER/$DIST_FILE_NAME.zip
DIST_UNZIPPED_FOLDER=$DIST_FOLDER/$DIST_FILE_NAME
OUTPUT_DIR=/home/play/$APP_NAME

PID_FILE=/home/play/$APP_NAME/RUNNING_PID

cd $DIST_FOLDER
rm -rf $DIST_UNZIPPED_FOLDER
sudo -u deploy unzip $DIST_FILE

#stop app
/usr/local/bin/deploy/stop-play-app.sh $APP_NAME
sudo -u play rm -f $PID_FILE

#renew lib/ and bin/
sudo -u play rm -rf $OUTPUT_DIR/lib $OUTPUT_DIR/bin
sudo -u play cp -r $DIST_UNZIPPED_FOLDER/lib $OUTPUT_DIR
sudo -u play cp -r $DIST_UNZIPPED_FOLDER/bin $OUTPUT_DIR

#start app again
/usr/local/bin/deploy/start-play-app.sh $APP_NAME

