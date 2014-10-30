#!/bin/bash
#usage dist-play-app app-name
#we assume here that app name is the same as the repository name

APP_NAME=$1
REPO_FOLDER=/home/mercurial/$APP_NAME
SOURCES_FOLDER=/home/play/$APP_NAME.sources
OUTPUT_FOLDER=/home/deploy/tmp/$APP_NAME
DIST_VERSION_FILE=$OUTPUT_FOLDER/.dist.local-revision-number

LOCAL_REVISION=`sudo -u mercurial hg id --num $REPO_FOLDER`

if [ -f $DIST_VERSION_FILE ] && [ "$LOCAL_REVISION" == `cat $DIST_VERSION_FILE` ]; then
  echo "Revision $LOCAL_REVISION already distributed"
  exit
fi

echo "Creating a distibution for revision $LOCAL_REVISION"

sudo -u play mkdir -p $SOURCES_FOLDER
sudo -u play rsync -az --delete --exclude=.hg $REPO_FOLDER/ $SOURCES_FOLDER
cd $SOURCES_FOLDER
sudo -u play play-framework clean
sudo -u play play-framework dist

#copy created zip to folder with distribution
ZIP_FOLDER=$SOURCES_FOLDER/target/universal
CREATED_ZIP=`ls $ZIP_FOLDER/*.zip` #returns the full path to the file
ZIP_FILE_NAME=`basename $CREATED_ZIP`
RAW_ZIP_FILE_NAME="${ZIP_FILE_NAME%.*}" #ZIP_FILE_NAME without extension

rm -rf $OUTPUT_FOLDER
sudo -u deploy mkdir -p $OUTPUT_FOLDER

#create file with distribution name
DISTRIBUTION_NAME_HINT=$OUTPUT_FOLDER/.dist.name
echo "$RAW_ZIP_FILE_NAME" > $DISTRIBUTION_NAME_HINT
chown deploy: $DISTRIBUTION_NAME_HINT
sudo -u deploy cp -f $CREATED_ZIP $OUTPUT_FOLDER

#write new revision name
echo $LOCAL_REVISION > $DIST_VERSION_FILE
chown deploy: $DIST_VERSION_FILE

#copy also public folder with assets
PUBLIC_FOLDER=$SOURCES_FOLDER/public
cp -r $PUBLIC_FOLDER $OUTPUT_FOLDER/
