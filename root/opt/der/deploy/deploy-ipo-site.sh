#!/bin/bash

SOURCES_FOLDER=$1
WWW_FOLDER=$2
WWW_USER=$3

#  --exclude .hg                                  \
#  --exclude .hgignore                            \
#  --exclude .idea                                \
#  --exclude *.iml                                \

rsync -a --stats --delete                \
  --exclude gallery_core/sql_config.php  \
  --exclude config2.php                  \
  --exclude db_config.php                \
                                         \
  --exclude temp                         \
                                         \
  --exclude gal_public/obloz             \
  --exclude gal_public/images            \
                                         \
  --exclude content                      \
  --include content/download.php         \
  --include content/.htaccess            \
  --include content/private/.htaccess    \
                                         \
  $SOURCES_FOLDER/journal/ $WWW_FOLDER/journal

# TODO probably exclude spaw2 uploads
rsync -a --stats --delete                \
  --exclude config.php                   \
                                         \
  $SOURCES_FOLDER/projects/ $WWW_FOLDER/projects

rsync -a --stats --delete                \
  $SOURCES_FOLDER/site/ $WWW_FOLDER/site


# change permissions and users for data folders
chown -R root: $WWW_FOLDER/journal
chown -R $WWW_USER: $WWW_FOLDER/journal/content
chown -R $WWW_USER: $WWW_FOLDER/journal/last_year.dat
chown -R $WWW_USER: $WWW_FOLDER/journal/gal_public/images
chown -R $WWW_USER: $WWW_FOLDER/journal/gal_public/obloz

chmod -R u=rwX,go=rX /var/www/html/journal/