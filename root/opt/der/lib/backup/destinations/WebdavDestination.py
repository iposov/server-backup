from Destination import Destination

import urlparse
import os
import pycurl

import xml.etree.ElementTree as ET
from StringIO import StringIO

class WebdavDestination(Destination):

    NAME = 'webdav'

    def __init__(self, context, destination_id, destination_description):
        Destination.__init__(self, context, destination_id, destination_description)

        self.url = destination_description[WebdavDestination.NAME]

        # parse path
        # todo get use of scheme
        parsed_url = urlparse.urlparse(self.url)
        self.remote_host = parsed_url.netloc

        self.path = parsed_url.path
        self.path = self.path.replace("$host", self.context.host)
        if not self.path.endswith('/'):
            self.path += '/'

        # empty params, query and fragment
        self.full_url = urlparse.urlunparse((parsed_url.scheme, self.remote_host, self.path, '', '', ''))

        auth = destination_description.get('auth', None)
        if auth is not None:
            self.credentials = self.context.credentials.get(auth, None)
            if self.credentials is None:
                self.context.log_error("credentials '%s' needed for webdav %s" % (auth, destination_id))

        self.ensure_folder_exists()


    def upload(self, local_path):
        file_name = os.path.basename(local_path)
        file_size = os.path.getsize(local_path)

        print "backup: Uploading file %s, size %d bytes" % (file_name, file_size)

        curl = None
        try:
            curl = pycurl.Curl()
            with open(local_path, 'rb') as file_object:
                curl.setopt(pycurl.URL, urlparse.urljoin(self.full_url, file_name))

                self._add_credentials(curl)

                curl.setopt(pycurl.UPLOAD, 1)
                curl.setopt(pycurl.READFUNCTION, file_object.read)
                curl.setopt(pycurl.INFILESIZE, file_size)

                curl.perform()
        #TODO handle CURL error
        except IOError as e:
            self.context.log_error("Failed to upload file " + file_name + " error: " + e.message)
        except pycurl.error as e:
            self.context.log_error("Failed to upload file " + file_name + " error: " + e.message)
        finally:
            if curl is not None:
                curl.close()

    def remove(self, file_name):
        pass

    def list_files(self):
        response = StringIO()
        curl = None
        try:
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, self.full_url)
            self._add_credentials(curl)

            # http://api.yandex.ru/disk/doc/dg/reference/propfind_contains-request.xml
            curl.setopt(pycurl.CUSTOMREQUEST, 'PROPFIND')
            curl.setopt(pycurl.HTTPHEADER, ['Depth: 1'])
            curl.setopt(pycurl.WRITEFUNCTION, response.write)

            curl.perform()

        #TODO handle CURL error
        except IOError as e:
            self.context.log_error("Failed to get folder contents: " + e.message)
            return []
        except pycurl.error as e:
            self.context.log_error("Failed to get folder contents: " + e.message)
            return []
        finally:
            if curl is not None:
                curl.close()

        # now parse response

        contents_xml = response.getvalue()
        try:
            root = ET.fromstring(contents_xml)
        except ET.ParseError:
            self.context.log_error("failed to parse response with the list of all backup files")
            return

        all_files = []
        # TODO is this DAV: prefix common for WebDAV or this is only from Yandex Disk
        for response_element in root.findall('{DAV:}response'):
            href = response_element.find('{DAV:}href')
            file_path = href.text
            _, file_name = os.path.split(file_path)
            all_files.append(file_name)

        return all_files


    def download(self, file_name, local_dir):
        #TODO test
        local_path = os.path.join(local_dir, file_name)
        remote_url = urlparse.urljoin(self.full_url, file_name)
        file_size = os.path.getsize(local_path)

        print "Downloading file %s" % file_name

        curl = None
        try:
            curl = pycurl.Curl()
            with open(local_path, 'wb') as file_object:
                curl.setopt(pycurl.URL, remote_url)

                self._add_credentials(curl)

                curl.setopt(pycurl.WRITEFUNCTION, file_object.write)

                curl.perform()
        #TODO handle CURL error
        except IOError as e:
            self.context.log_error("Failed to download file " + file_name + " error: " + e.message)
        except pycurl.error as e:
            self.context.log_error("Failed to download file " + file_name + " error: " + e.message)
        finally:
            if curl is not None:
                curl.close()


    def ensure_folder_exists(self):
        curl = None
        try:
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, self.full_url)

            self._add_credentials(curl)
            curl.setopt(pycurl.CUSTOMREQUEST, "MKCOL")

            curl.perform()

            http_result_code = curl.getinfo(pycurl.HTTP_CODE)

            if http_result_code == 201:
                self.context.log("Remote folder %s created" % self.path)
            elif http_result_code == 405:
                self.context.log("Remote folder %s already exists" % self.path)
            else:
                self.context.log_error("Got http response %d while creating remote folder %s" % (http_result_code, self.path))

        #TODO handle CURL error
        except IOError as e:
            self.context.log_error("Failed to create remote folder " + e.message)
        except pycurl.error as e:
            self.context.log_error("Failed to create remote folder " + e.message)
        finally:
            if curl is not None:
                curl.close()

    def _add_credentials(self, curl):
        if self.credentials is not None:
            curl.setopt(pycurl.USERPWD, self.credentials['login'] + ':' + self.credentials['password'])