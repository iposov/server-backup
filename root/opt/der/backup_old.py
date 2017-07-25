#!/usr/bin/python
import os
import pycurl
import sys
import xml.etree.ElementTree as ET
from StringIO import StringIO

import yaml

# TODO encrypt backups, use gpg with an asymmetric key
# TODO save output to log
from lib.backup.BackupContext import BackupContext
from lib.backup.TarArchive import TarArchive


def read_webdav_config(webdav_key):
    try:
        with open(DESTINATIONS_FILE) as cfg_file:
            cfg = yaml.load(cfg_file)
            if webdav_key not in cfg:
                print >> sys.stderr, "Failed to find webdav credentials for key " + webdav_key
                sys.exit(4)
            cfg = cfg[webdav_key]
    except IOError:
        print >> sys.stderr, "Failed to read file with WebDAV credentials " + DESTINATIONS_FILE
        sys.exit(5)

    return cfg


def webdav_url(webdav_config):
    # returns url, and boolean, indicating weather it has a subfolder
    url = webdav_config['url']
    if 'subfolder' in webdav_config:
        sub = webdav_config['subfolder']
        if sub == '$host':
            sub = HOST
        url += '/' + sub
        return url, True
    else:
        return url, False


def upload_to_webdav(webdav_config):
    print "backup: Uploading started"

    url, has_subfolder = webdav_url(webdav_config)
    if has_subfolder:
        # create subdirectory
        # http://api.yandex.ru/disk/doc/dg/reference/mkcol.xml
        curl = None
        try:
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, url)

            curl.setopt(pycurl.USERPWD, webdav_config['login'] + ':' + webdav_config['password'])
            curl.setopt(pycurl.CUSTOMREQUEST, "MKCOL")

            curl.perform()

            # TODO test return code: 201 - ok, 405 - already exists (?) or some other problem
        except IOError as e:
            print >> sys.stderr, "Failed to create remote folder " + e.message
            sys.exit(6)
        finally:
            if curl is not None:
                curl.close()

    # list all files
    all_tar_files = [f for f in os.listdir(TEMP_DIR) if f.endswith(".tar.gz")]  # TODO change condition

    # upload each file separately
    for file_to_upload_name in all_tar_files:
        print "backup: Uploading file " + file_to_upload_name

        file_to_upload_path = TEMP_DIR + '/' + file_to_upload_name
        file_size = os.path.getsize(file_to_upload_path)
        curl = None
        try:
            curl = pycurl.Curl()
            with open(file_to_upload_path, 'rb') as file_object:
                curl.setopt(pycurl.URL, url + '/' + file_to_upload_name)

                curl.setopt(pycurl.USERPWD, webdav_config['login'] + ':' + webdav_config['password'])

                curl.setopt(pycurl.UPLOAD, 1)
                curl.setopt(pycurl.READFUNCTION, file_object.read)
                curl.setopt(pycurl.INFILESIZE, file_size)

                curl.perform()
        except IOError as e:
            print >> sys.stderr, "Failed to upload file " + file_to_upload_name + " error: " + e.message
        finally:
            if curl is not None:
                curl.close()

def file_needs_to_be_removed(date):
    # we remove files with dates older than 31 day before today, excluding the first days of months
    delta = NOW - date
    return delta.days > 31 and date.day != 1


def clear_old_files(webdav_config):
    url, _ = webdav_url(webdav_config)

    # first, read folder contents
    response = StringIO()

    curl = None
    try:
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)

        curl.setopt(pycurl.USERPWD, webdav_config['login'] + ':' + webdav_config['password'])

        # http://api.yandex.ru/disk/doc/dg/reference/propfind_contains-request.xml
        curl.setopt(pycurl.CUSTOMREQUEST, 'PROPFIND')
        curl.setopt(pycurl.HTTPHEADER, ['Depth: 1'])
        curl.setopt(pycurl.WRITEFUNCTION, response.write)

        curl.perform()
    except IOError as e:
        print >> sys.stderr, "Failed to get folder contents: " + e.message
    finally:
        if curl is not None:
            curl.close()

    contents_xml = response.getvalue()
    try:
        root = ET.fromstring(contents_xml)
    except ET.ParseError:
        print >> sys.stderr, "failed to parse response with the list of all backup files"
        return

    # select files from response
    all_files = []
    # TODO is this DAV: prefix common for WebDAV or this is only from Yandex Disk
    for response_element in root.findall('{DAV:}response'):
        href = response_element.find('{DAV:}href')
        file_path = href.text
        _, file_name = os.path.split(file_path)
        all_files.append(file_name)

    files_with_dates = [(file_name, date) for file_name, date in map(lambda f: (f, file_date(f)), all_files) if
                        date is not None]

    files_to_delete = [file_name for file_name, date in files_with_dates if file_needs_to_be_removed(date)]

    # now delete all the files
    if len(files_to_delete) > 0:
        print "backup: Going to delete old files:"
    else:
        print "backup: No old files to delete"

    for file_to_delete in files_to_delete:
        print "backup: Deleting file " + file_to_delete
        delete_url = url + '/' + file_to_delete

        curl = None
        try:
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, delete_url)

            curl.setopt(pycurl.USERPWD, webdav_config['login'] + ':' + webdav_config['password'])

            curl.setopt(pycurl.CUSTOMREQUEST, 'DELETE')

            curl.perform()
        except IOError as e:
            print >> sys.stderr, "Failed to delete file: " + delete_url + " message: " + e.message
        finally:
            if curl is not None:
                curl.close()

    print "backup: Finished deleting files"

if __name__ == '__main__':
    with BackupContext() as context:
        targets = context.get_targets()
        destinations = context.get_destinations()

        if not targets:
            print >> sys.stderr, "Unknown target {0}".format(context.target_name)
            sys.exit(2)

        if not targets:
            print >> sys.stderr, "Unknown destination {0}".format(context.target_name)
            sys.exit(3)

        tar_archives = []
        for target in targets:
            tar_path = target.tar_path()
            with TarArchive(tar_path) as tar_archive:
                tar_elements = target.run()
                for tar_element in tar_elements:
                    context.log('taring %s' % tar_element.description())
                    tar_archive.add(tar_element)
                tar_archives.append(tar_archive)

        #TODO destination send
        for destination in destinations:
            for tar_archive in tar_archives:
                destination.send()


        # upload_to_webdav(_webdav_config)
        # clear_old_files(_webdav_config)
