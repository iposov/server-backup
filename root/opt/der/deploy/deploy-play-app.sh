#!/bin/bash
#usage deploy-play-app app-name

APP_NAME=$1
#dist app name is a name of folder with a source application
DIST_APP_NAME=$2

if [ -z "$DIST_APP_NAME" ]; then
    DIST_APP_NAME=$APP_NAME
fi

DIST_FOLDER=/home/deploy/tmp/$DIST_APP_NAME

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
/opt/der/deploy/stop-play-app.sh $APP_NAME
sudo -u play rm -f $PID_FILE

#renew lib/ and bin/ and public/
sudo -u play rm -rf $OUTPUT_DIR/lib $OUTPUT_DIR/bin $OUTPUT_DIR/public
sudo -u play cp -r $DIST_UNZIPPED_FOLDER/lib $OUTPUT_DIR
sudo -u play cp -r $DIST_UNZIPPED_FOLDER/bin $OUTPUT_DIR
sudo -u play cp -r $DIST_FOLDER/public $OUTPUT_DIR

#rename boot script
sudo -u play cp $OUTPUT_DIR/bin/$DIST_APP_NAME $OUTPUT_DIR/bin/$APP_NAME

#start app again
/opt/der/deploy/start-play-app.sh $APP_NAME
