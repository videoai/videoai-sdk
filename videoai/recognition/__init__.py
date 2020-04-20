#!/usr/bin/python
# -*- coding: latin-1 -*-

__author__ = 'kieron'

from videoai import VideoAIUser, print_http_response, SIGN_REQUEST, Error, FailedAPICall, VERIFY_SSL, get_parameter

import json
import requests
import datetime
from os.path import expanduser
from configparser import ConfigParser
import os
import hashlib

#from ..logger import console_logger, file_logger

# get rid of annoying message about using unverified certificates
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class WatchlistNotFound(Error):
    """Watchlist not found"""


class Recognition(VideoAIUser):
    def __init__(self, token, host, authentication_server, client_id, client_secret, verbose=False):
        super(Recognition, self).__init__(token=token,
                                          host=host,
                                          authentication_server=authentication_server,
                                          client_id=client_id,
                                          client_secret=client_secret,
                                          verbose=verbose)
        self.subject = 'subject'
        self.description = 'description'
        self.sighting = 'sighting'
        self.watchlist = 'watchlist'
        self.subject_watchlist = 'subject_watchlist'

    def subject_thumbnail(self, subject_id, request=None):
        url = '{}/{}/{}'.format(self.base_url, 'thumbnail/subject', subject_id)

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)

        #if True:
        #    print print_http_response(r)

        if r.status_code == 200:
            return r.content
        else:
            return ""

    def description_thumbnail(self, description_id, request=None):
        url = '{}/{}/{}'.format(self.base_url, 'thumbnail/description', description_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)
        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
        if self.verbose:
            print(print_http_response(r))
        return r.content

    def get_sighting(self, sighting_id, request=None):
        url = '{}/sighting/{}'.format(self.base_url, sighting_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)
        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
        if self.verbose:
            print(print_http_response(r))
        return r.json()

    def hide_sighting(self, sighting_id, request=None):
        url = '{}/hide/{}'.format(self.base_url, sighting_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)
        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
        if self.verbose:
            print(print_http_response(r))
        return r.json()


    def confirm_sighting_identity(self, sighting_id, subject_id, request=None):
        url = '{}/sighting/{}/{}/true'.format(self.base_url, sighting_id, subject_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)
        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
        if self.verbose:
            print(print_http_response(r))
        return r.json()

    def reject_sighting_identity(self, sighting_id, subject_id, request=None):
        url = '{}/sighting/{}/{}/false'.format(self.base_url, sighting_id, subject_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)
        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
        if self.verbose:
            print(print_http_response(r))
        return r.json()

    def sighting_thumbnail(self, sighting_id, request=None):
        url = '{}/{}/{}'.format(self.base_url, 'thumbnail/sighting', sighting_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)
        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)

        if r.status_code != 200:
            return ""
        if self.verbose:
            print(print_http_response(r))
        return r.content

    def set_thumbnail(self, subject_id, sighting_id, request=None):
        url = '{}/thumbnail/{}/{}'.format(self.base_url, subject_id, sighting_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="POST", request=request)
        r = requests.post(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
        if self.verbose:
            print(print_http_response(r))
        return r.json()

    def sighting_acknowledge(self, sighting_id, request=None):
        url = '{}/sighting/{}/acknowledge'.format(self.base_url, sighting_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)
        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
        if self.verbose:
            print(print_http_response(r))
        return r.content

    def sighting_true(self, sighting_id, request=None):
        url = '{}/sighting/{}/true'.format(self.base_url, sighting_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)
        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
        if self.verbose:
            print(print_http_response(r))
        return r.content

    def sighting_error(self, sighting_id, request=None):
        url = '{}/sighting/{}/error'.format(self.base_url, sighting_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)
        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
        if self.verbose:
            print(print_http_response(r))
        return r.content

    def add_sighting(self, data, request=None):

        url = "{}/{}".format(self.base_url, self.sighting)
        if SIGN_REQUEST:
            self.sign_request(url, data=data, method="POST", request=request)
        r = requests.post(url, headers=self.header, data=data,  allow_redirects=True, verify=VERIFY_SSL)
        if self.verbose:
            print(print_http_response(r))
        return r.json()


    def create_subject(self,
                       name,
                       watchlist='',
                       watchlist_data='',
                       subject_data='',
                       sighting_id='',
                       request=None):
        """
        Create a new subject
        :param name: a name to give the subject
        :param subject_data: a dictionary of data to store with a subject 
        :param watchlist: a single watchlist-id to add and associate to the created subject
        :param watchlist_data: a dictionary of watchlist-ids, this will get stored as JSON
        :param sighting_id: a single sighting-id to associate to the created subject
        :return: subject_id: The subject_id of the created subject
        """
        url = "{0}/{1}".format(self.base_url, self.subject)

        # always need a name 
        data = {'name': name }

        # for subject data we need to convert whatever object to a str/unicode
        if subject_data:
            d = dict()
            for key, value in subject_data.iteritems():
                if isinstance(value, int):
                    d['{}::int'.format(key)] = str(value)
                elif isinstance(value, float):
                    d['{}::float'.format(key)] = str(value)
                elif isinstance(value, basestring):  # str or unicode
                    if len(key.split('::')) == 2:
                        d[key] = value
                    else:
                        d['{}::string'.format(key)] = value
                elif isinstance(value, datetime.date):
                    d['{}::date'.format(key)] = value.isoformat()
                elif isinstance(value, list):
                    d['{}::list'.format(key)] = [unicode(i) for i in value]
                else:
                    print 'Unknown value type'
            data['subject_data'] = json.dumps(d, ensure_ascii=False)

        if sighting_id:
            data['sighting_id'] = sighting_id

        # if we have a valid watchlist then we try and use it
        if watchlist:
            data['watchlist'] = watchlist

        if watchlist_data:
            data['watchlist_data'] = json.dumps(watchlist_data)

        if SIGN_REQUEST:
            self.sign_request(url, data=data, method="POST", request=request)
        r = requests.post(url, headers=self.header, data=data, allow_redirects=True, verify=VERIFY_SSL)

        if self.verbose:
            print(print_http_response(r))

            # if r.json()['status'] != 'success':
            # raise Exception("Create subject failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

    def edit_subject_watchlist(self, subject_id, watchlist_ids=[], watchlist_ids_to_add='',
                               watchlist_ids_to_remove='', request=None):
        """
        Edit an existing subject
        """
        url = "{0}/{1}/{2}/watchlist".format(self.base_url, self.subject, subject_id)
        data = {}

        if watchlist_ids:
            data['watchlist_ids'] = json.dumps(watchlist_ids)

        if watchlist_ids_to_add:
            data['watchlist_ids_to_add'] = json.dumps(watchlist_ids_to_add)

        if watchlist_ids_to_remove:
            data['watchlist_ids_to_remove'] = json.dumps(watchlist_ids_to_remove)

        if SIGN_REQUEST:
            self.sign_request(url, data=data, method="PUT", request=request)
        r = requests.put(url, headers=self.header, data=data, allow_redirects=True, verify=VERIFY_SSL)

        if r.json()['status'] != 'success':
            print(r.text)
            # raise Exception("Edit subject failed: {}". format(r.json()['message']))

        if self.verbose:
            print(print_http_response(r))

        return r.json()


    def edit_subject(self, subject_id, name='', subject_data='', request=None):
        """
        Edit an existing subject
        """
        url = "{0}/{1}/{2}".format(self.base_url, self.subject, subject_id)
        data = {}

        if name:
            data['name'] = name

        # for subject data we need to convert whatever object to a str/unicode
        if subject_data:
            d = dict()            
            for key,value in subject_data.items():
                if isinstance(value, int):
                    d['{}::int'.format(key)] = str(value)
                elif isinstance(value, float):
                    d['{}::float'.format(key)] = str(value)
                elif isinstance(value, str): # str or unicode
                    d['{}::string'.format(key)] = value 
                elif isinstance(value, datetime.date):
                    d['{}::date'.format(key)] = value.isoformat()
                elif isinstance(value, list):
                    d['{}::list'.format(key)] = [str(i) for i in value]
                else:
                    print('Unknown value type')
            data['subject_data'] = json.dumps(d, ensure_ascii=False)


        if SIGN_REQUEST:
            self.sign_request(url, data=data, method="PUT", request=request)
        r = requests.put(url, headers=self.header, data=data, allow_redirects=True, verify=VERIFY_SSL)

        if r.json()['status'] != 'success':
            print(r.text)
            # raise Exception("Edit subject failed: {}". format(r.json()['message']))

        if self.verbose:
            print(print_http_response(r))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()


    def get_subject(self, subject_id, no_sighting=False, request=None):
        """
        Get a subject
        """
        url = "{0}/{1}/{2}?no_sighting={3}".format(self.base_url, self.subject, subject_id, no_sighting)

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
        if r.json()['status'] != 'success':
            print(r.text)
            # raise Exception("Get subject failed: {}". format(r.json()['message']))

        if self.verbose:
            print(print_http_response(r))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()


    def delete_subject(self, subject_id, request=None):
        """
        Delete a subject
        :param subject_id: The subject id
        :return:
        """
        url = "{0}/{1}/{2}".format(self.base_url, self.subject, subject_id)

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="DELETE", request=request)
        r = requests.delete(url, headers=self.header, verify=VERIFY_SSL)

        if self.verbose:
            print(print_http_response(r))

        if r.json()['status'] != 'success':
            print(r.text)
            # raise Exception("Deleted subject failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

    def delete_subjects(self, watchlist_ids=[]):
        """
        Delete all the subjects
        :param watchlist_ids:  Only delete subjects in these watchlists
        :return: list of subject_ids that have been deleted
        """
        subjects = []
        response = self.list_subjects(watchlist_data=watchlist_ids)
        if response['status'] == "success":
            subjects = response['data']['subjects']
        subjects_deleted = []
        for subject in subjects:
            subject_id = subject['subject_id']
            try:
                self.delete_subject(subject_id)
                subjects_deleted.append(subject_id)
            except:
                print('Trouble deleting subject "{}"'.format(subject_id))

        return subjects_deleted

    def list_deleted_subjects(self, data={}, request=None):
        """
        List all deleted subjects
        :return:
        """

        url = "{}/{}/deleted".format(self.base_url, self.subject)
        sep = "?"
        if data is not None and len(data) > 0:
            for i, v in enumerate(data):
                if data[v] is not None:
                    url += sep + v + "=" + str(data[v])
                    sep = "&"

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

        r = requests.get(url, headers=self.header, verify=VERIFY_SSL)

        if self.verbose:
            print(print_http_response(r))

        if r.json()['status'] != 'success':
            print(r.text)
            # raise Exception("Create subject failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

    def list_subjects(self, page=1,
                      number_per_page=1000, 
                      data={},
                      watchlist='',
                      watchlist_data='',
                      request=None
                      ):
        """
        List all the subjects
        :param watchlist_ids: If specified then filter by these watchlist_ids
        :return:
        """
        wl_ids = []

        # if we have a valid watchlist then we try and use it
        if watchlist:
            wl_ids.append(str(watchlist))

        if watchlist_data:
            wl_ids.extend(watchlist_data)

        url = "{}/{}/{}/{}?watchlist_data={}".format(self.base_url, self.subject, page, number_per_page, json.dumps(wl_ids))
        sep = "&"
        if data is not None and len(data) > 0:
            for i, v in enumerate(data):
                if data[v] is not None:
                    url += sep + v + "=" + str(data[v])
                    sep = "&"

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

        r = requests.get(url, headers=self.header, verify=VERIFY_SSL)

        if self.verbose:
            print(print_http_response(r))

        if r.json()['status'] != 'success':
            print(r.text)
            # raise Exception("Create subject failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

    def get_updated_subject_from_list_and_timestamp(self, subject_list, timestamp, request=None):

        url = "{}/{}/updated".format(self.base_url, self.subject)

        data = {'subject_list': json.dumps(subject_list), 'timestamp': timestamp}

        if SIGN_REQUEST:
            self.sign_request(url, data=data, method="POST", request=request)

        r = requests.post(url, data=data, headers=self.header, verify=VERIFY_SSL)

        if self.verbose:
            print(print_http_response(r))

        if r.json()['status'] != 'success':
            print(r.text)
            # raise Exception("Create subject failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

    def get_subject_status(self, verbose=False, last_update=None, request=None):
        url = "{}/subject_status".format(self.base_url)

        data = {'verbose': verbose}
        if last_update is not None:
            try:
                data['last_update'] = int(last_update)
            except Exception as e:
                print(("Exception in SDK get_subject_status: last_update is not an integer ({})".format(last_update)))

        if SIGN_REQUEST:
            self.sign_request(url, data=data, method="POST", request=request)

        r = requests.post(url, data=data, headers=self.header, verify=VERIFY_SSL)

        if self.verbose:
            print(print_http_response(r))

        if r.json()['status'] != 'success':
            print(r.text)
            # raise Exception("Create subject failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

    def get_descriptor(self, description_id, with_thumbnail=False, request=None):
        url = "{}/descriptor/{}?with_thumbnail={}".format(self.base_url, description_id, with_thumbnail)

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

        r = requests.get(url, headers=self.header, data=None, verify=VERIFY_SSL)

        try:
            if r.headers['md5'] is not None:
                md5 = hashlib.md5(r.text).hexdigest()
                if md5 != r.headers['md5']:
                    print("MD5  NOT  OK")
        except Exception as e:
            print(("Exception in SDK get_descriptor while checking md5 ({})".format(e)))

        if self.verbose:
            print(print_http_response(r))

        if r.json()['status'] != 'success':
            print(r.text)
            raise Exception("Get description failed: {}".format(r.json()['message']))

        return r.json()

    def get_descriptors_number(self, request=None):
        """
        List all the descriptions in the database
        :param description_id: The description you want to get
        :return:
        """
        url = "{}/descriptors_number".format(self.base_url, self.description)

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

        r = requests.get(url, headers=self.header, data=None, verify=VERIFY_SSL)

        #self.verbose = True
        if self.verbose:
            print(print_http_response(r))

        if r.json()['status'] != 'success':
            print(r.text)
            raise Exception("Get description number failed: {}".format(r.json()['message']))

        return r.json()

    def get_description(self,
                        description_id,
                        request=None
    ):
        """
        List all the descriptions in the database
        :param description_id: The description you want to get 
        :return:
        """
        url = "{}/{}/{}".format(self.base_url, self.description, description_id)

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

        r = requests.get(url, headers=self.header, data=None, verify=VERIFY_SSL)
        
        self.verbose=True
        if self.verbose:
            print(print_http_response(r))

        if r.json()['status'] != 'success':
            print(r.text)
            raise Exception("Get description failed: {}". format(r.json()['message']))

        return r.json()


    def list_descriptions(self, 
                          page=1,
                          number_per_page=1000, 
                          updated=None,
                          base64=False,
                          request=None
    ):
        """
        List all the descriptions in the database
        :param updated: Time in UTC . 
        :param base64: Get base64 data of the description
        :return:
        """
        url = "{}/{}/{}/{}".format(self.base_url, self.description, page, number_per_page)
        data = {
            'base64': str(base64)
        }

        if updated is not None:
           data['updated'] = updated.isoformat()

        if SIGN_REQUEST:
            self.sign_request(url, data=data, method="GET", request=request)

        r = requests.get(url, headers=self.header, data=data, verify=VERIFY_SSL)
        
        if self.verbose:
            print(print_http_response(r))

        if r.json()['status'] != 'success':
            print(r.text)
            raise Exception("List descriptions failed: {}". format(r.json()['message']))

        return r.json()

    def enrol_from_image(self, subject_id, image_file, request=None):
        pass

    # link sighting to subject without adding the description
    def link_sighting_to_subject(self, sighting_id, subject_id, request):
        url = "{0}/{1}/{2}/{3}".format(self.base_url, self.subject, sighting_id, subject_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="POST", request=request)
        r = requests.post(url, headers=self.header, verify=VERIFY_SSL)

        if self.verbose:
            print(print_http_response(r))

        if r.json()['status'] != 'success':
            print(r.text)
            # raise Exception("Add sighting to subject failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

    # Returns job_id if task has been successfully launched
    # raise an error instead
    def add_sighting_to_subject(self, sighting_id, subject_id, request=None):
        url = "{0}/{1}/{2}/{3}".format(self.base_url, self.sighting, sighting_id, subject_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="POST", request=request)
        r = requests.post(url, headers=self.header, verify=VERIFY_SSL)

        if self.verbose:
            print(print_http_response(r))

        if r.json()['status'] != 'success':
            print(r.text)
            # raise Exception("Add sighting to subject failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

    def list_sightings(self, page=1, number_per_page=1000, data={}, request=None):
        """
        Get sightings
        :return:
        """
        url = "{}/{}/{}/{}".format(self.base_url, self.sighting, page, number_per_page)
        sep = "?"
        if data is not None and len(data) > 0:
            for i, v in enumerate(data):
                if data[v] is not None:
                    url += sep + v + "=" + str(data[v])
                    sep = "&"

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

        try:
            r = requests.get(url, headers=self.header, verify=VERIFY_SSL)
        except Exception as e:
            data = {}
            data['success'] = 'failed'
            data['data'] = ""
            return json.dumps(data)

        if self.verbose:
            print(print_http_response(r))
            # raise Exception("List sightings: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

    def add_description(self, subject_id, description_id):
        pass

    def delete_description(self, description_id, request=None):
        url = "{0}/{1}/{2}".format(self.base_url, self.description, description_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="DELETE", request=request)
        r = requests.delete(url, headers=self.header, verify=VERIFY_SSL)

        if self.verbose:
            print(print_http_response(r))

        if r.json()['status'] != 'success':
            print(r.text)
            # raise Exception("Failed to delete description: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()


    # list all available watchlist
    def list_watchlists(self, ignore_unknown=False, request=None):
        url = "{0}/{1}".format(self.base_url, self.watchlist)
        #print("---->>+++ THE url {} / {}".format(url, console_logger))
        #console_logger.info("--dsadsadsadsa-->>+++ THE url {}".format(url))
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

        r = requests.get(url, headers=self.header, verify=VERIFY_SSL)
        if self.verbose:
            print(print_http_response(r))

        json_resp = r.json()
        if json_resp['status'] != 'success':
            print(r.text)

        if json_resp['status'] == 'success' and ignore_unknown:
            watchlists = []
            for watchlist in json_resp['data']['watchlists']:
                if watchlist['name'] != 'Unknown':
                    watchlists.append(watchlist)
            # return watchlists
            json_resp['data']['watchlists'] = watchlists

        return json_resp

    def delete_watchlists(self, request=None):
        """
        Delete all the watchlists
        :param
        :return:
        """
        watchlists = self.list_watchlists()['data']['watchlists']
        for watchlist in watchlists:
            self.delete_watchlist(watchlist['id'])



    def delete_watchlist(self, watchlist_id, request=None):
        """
        Delete a watchlist
        :param watchlist_id: The watchlist id
        :return:
        """
        url = "{0}/{1}/{2}".format(self.base_url, self.watchlist, watchlist_id)

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="DELETE", request=request)
        r = requests.delete(url, headers=self.header, verify=VERIFY_SSL)

        if self.verbose:
            print(print_http_response(r))

        if r.json()['status'] != 'success':
            print(r.text)
        return r.json()

    def watchlist_id(self, watchlist_name):
        watchlists = self.list_watchlists(ignore_unknown=True)
        if watchlists['status'] != 'success':
            raise FailedAPICall('list_watchlist')

        watchlists = watchlists['data']['watchlists']
        watchlist_id = None
        for watchlist in watchlists:
            if watchlist['name'] == watchlist_name:
                watchlist_id = watchlist['id']
                break
        if watchlist_id is None:
            raise WatchlistNotFound(watchlist_name)
        return watchlist_id

    def get_watchlist_ids(self):
        watchlists = self.list_watchlists(ignore_unknown=True)['data']['watchlists']
        watchlist_ids = [x['id'] for x in watchlists]
        return watchlist_ids

    def create_watchlist_for_unittest(self, watchlist=None, request=None):
        '''
        Initialize unittest on analytics database -> watchlist
        :return:
        '''
        watchlist_list = self.list_watchlists()
        if watchlist_list['status'] == 'success':
            watchlist_list = watchlist_list['data']['watchlists']
        watchlist_name_list = []
        for w in watchlist_list:
            watchlist_name_list.append(w['name'])

        response = None
        need_to_create = False
        for w in watchlist:
            if w['name'] not in watchlist_name_list:
                need_to_create = True
                url = '{}/watchlist'.format(self.base_url)
                self.sign_request(url=url, data=w, method='POST', request=request)
                response = requests.post(url, w, headers=self.header, verify=VERIFY_SSL)
                json_response = json.loads(response.text)
                if self.verbose:
                    print(print_http_response(response))

        if not need_to_create:
            return True, json.dumps({'status': 'success'}), None
        if response and response.status_code == 200:
            return True, response.content, response.headers
        else:
            return False, None, None

    def assign_watchlist_to_user_for_unittest(self, email, watchlist=None, request=None):
        '''
        Initialize unittest on authentication database
        :return:
        '''

        watchlist_list = self.list_watchlists()
        if watchlist_list['status'] == 'success':
            watchlist_list = watchlist_list['data']['watchlists']

        built_watchlist = []
        for w in watchlist:
            name = w['name']
            built_watchlist.append((item for item in watchlist_list if item["name"] == name).next()['id'])

        data = {'email': email, 'watchlist': json.dumps(built_watchlist)}
        url = '{}/auth/assign_watchlist_to_user_for_unittest'.format(self.authentication_server)
        self.sign_request(url=url, data=data, method='POST', request=request)
        response = requests.post(url, data, headers=self.header, verify=VERIFY_SSL)
        json_response = json.loads(response.text)
        if self.verbose:
            print(print_http_response(response))

        if response.status_code == 200:
            return True, response.content, response.headers
        else:
            return False, None, None



