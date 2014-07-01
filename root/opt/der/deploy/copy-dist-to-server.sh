#!/bin/bash
#usage copy-dist-to-server dist-name server-name

DIST_NAME=$1
SERVER_NAME=$2
sudo -u mercurial rsync -az --delete /home/deploy/tmp/$DIST_NAME/ deploy@$SERVER_NAME:/home/deploy/tmp/$DIST_NAME

