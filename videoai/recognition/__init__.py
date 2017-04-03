__author__ = 'kieron'

from videoai import VideoAIUser, print_http_response, SIGN_REQUEST, Error, FailedAPICall
import json
import requests

class WatchlistNotFound(Error):
    """Watchlist not found"""


class Recognition(VideoAIUser):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(Recognition, self).__init__(token=token,
                                          host=host,
                                          client_id=client_id,
                                          client_secret=client_secret,
                                          verbose=verbose)
        self.subject = 'subject'
        self.description = 'description'
        self.sighting = 'sighting'
        self.watchlist = 'watchlist'
        self.watchlisted = 'watchlisted'

    def subject_thumbnail(self, subject_id):
        url = '{}/{}/{}'.format(self.base_url, 'thumbnail/subject', subject_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET")
        print url

        r = requests.get(url, headers=self.header, allow_redirects=True)

        if self.verbose:
            print print_http_response(r)

        if r.status_code == 200:
            return r.content
        else:
            return ""

    def description_thumbnail(self, description_id):
        url = '{}/{}/{}'.format(self.base_url, 'thumbnail/description', description_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET")
        r = requests.get(url, headers=self.header, allow_redirects=True)
        if self.verbose:
            print print_http_response(r)
        return r.content

    def sighting_thumbnail(self, sighting_id):
        url = '{}/{}/{}'.format(self.base_url, 'thumbnail/sighting', sighting_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET")
        r = requests.get(url, headers=self.header, allow_redirects=True)

        if r.status_code != 200:
            return ""
        if self.verbose:
            print print_http_response(r)
        return r.content


    def sighting_acknowledge(self, sighting_id):
        url = '{}/sighting/{}/acknowledge'.format(self.base_url, sighting_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET")
        r = requests.get(url, headers=self.header, allow_redirects=True)
        if self.verbose:
            print print_http_response(r)
        return r.content

    def sighting_true(self, sighting_id):
        url = '{}/sighting/{}/true'.format(self.base_url, sighting_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET")
        r = requests.get(url, headers=self.header, allow_redirects=True)
        if self.verbose:
            print print_http_response(r)
        return r.content

    def sighting_error(self, sighting_id):
        url = '{}/sighting/{}/error'.format(self.base_url, sighting_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET")
        r = requests.get(url, headers=self.header, allow_redirects=True)
        if self.verbose:
            print print_http_response(r)
        return r.content

    def create_subject(self,
                       name,
                       watchlist='',
                       watchlist_data='',
                       user_data={'gender': 'Unknown', 'notes': ''},
                       sighting_id=''):
        """
        Create a new subject
        :param name: a name to give the subject
        :param user_data: a dictionary of user data, this will get stored as JSON
        :param watchlist: a single watchlist-id to add and associate to the created subject
        :param watchlist_data: a dictionary of watchlist-ids, this will get stored as JSON
        :param sighting_id: a single sighting-id to associate to the created subject
        :return: subject_id: The subject_id of the created subject
        """
        url = "{0}/{1}".format(self.base_url, self.subject)

        json_user_data = json.dumps(user_data, ensure_ascii=False)

        data = {'name': name, 'user_data': json_user_data}

        if sighting_id:
            data['sighting_id'] = sighting_id

        # if we have a valid watchlist then we try and use it
        if watchlist:
            data['watchlist'] = watchlist

        if watchlist_data:
            data['watchlist_data'] = json.dumps(watchlist_data)

        if SIGN_REQUEST:
            self.sign_request(url, data=data, method="POST")
        r = requests.post(url, headers=self.header, data=data, allow_redirects=True)

        if self.verbose:
            print print_http_response(r)

            # if r.json()['status'] != 'success':
            # raise Exception("Create subject failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()


    def edit_subject_watchlist(self, subject_id, watchlist_ids=[], watchlist_ids_to_add='', watchlist_ids_to_remove=''):
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
            self.sign_request(url, data=data, method="PUT")
        r = requests.put(url, headers=self.header, data=data, allow_redirects=True)

        if r.json()['status'] != 'success':
            print r.text
            # raise Exception("Edit subject failed: {}". format(r.json()['message']))

        if self.verbose:
            print print_http_response(r)

        return r.json()


    def edit_subject(self, subject_id, name='', user_data={}):
        """
        Edit an existing subject
        """
        url = "{0}/{1}/{2}".format(self.base_url, self.subject, subject_id)
        data = {}

        if name:
            data['name'] = name

        if user_data:
            data['user_data'] = json.dumps(user_data)


        if SIGN_REQUEST:
            self.sign_request(url, data=data, method="PUT")
        r = requests.put(url, headers=self.header, data=data, allow_redirects=True)

        if r.json()['status'] != 'success':
            print r.text
            # raise Exception("Edit subject failed: {}". format(r.json()['message']))

        if self.verbose:
            print print_http_response(r)

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()


    def get_subject(self, subject_id):
        """
        Get a subject
        """
        url = "{0}/{1}/{2}".format(self.base_url, self.subject, subject_id)

        print url

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET")

        r = requests.get(url, headers=self.header, allow_redirects=True)


        if r.json()['status'] != 'success':
            print r.text
            # raise Exception("Get subject failed: {}". format(r.json()['message']))

        #if self.verbose:
        print print_http_response(r)

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()


    def delete_subject(self, subject_id):
        """
        Delete a subject
        :param subject_id: The subject id
        :return:
        """
        url = "{0}/{1}/{2}".format(self.base_url, self.subject, subject_id)

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="DELETE")
        r = requests.delete(url, headers=self.header)

        if self.verbose:
            print print_http_response(r)

        if r.json()['status'] != 'success':
            print r.text
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
                print 'Trouble deleting subject "{}"'.format(subject_id)

        return subjects_deleted

    def list_subjects(self, page=1, 
                      number_per_page=1000, 
                      data={},
                      watchlist='',
                      watchlist_data=''
                      ):
        """
        List all the subjects
        :param watchlist_ids: If specified then filter by these watchlist_ids
        :return:
        """
        wl_ids = []

        # if we have a valid watchlist then we try and use it
        if watchlist:
            print 'appending {}'.format(watchlist)
            wl_ids.append(unicode(watchlist))

        if watchlist_data:
            wl_ids.extend(watchlist_data)

        url = u"{}/{}/{}/{}?watchlist_data={}&gender_male=false&gender_female=false".format(self.base_url, self.subject, page, number_per_page, json.dumps(wl_ids))
        sep = "?"
        if data is not None and len(data) > 0:
            for i, v in enumerate(data):
                if data[v] is not None:
                    url += sep + v + "=" + unicode(data[v])
                    sep = "&"

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET")

        r = requests.get(url, headers=self.header)

        if self.verbose:
            print print_http_response(r)

        if r.json()['status'] != 'success':
            print r.text
            # raise Exception("Create subject failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()


    def enrol_from_image(self, subject_id, image_file):
        pass

    # Returns job_id if task has been successfully launched
    # raise an error instead
    def add_sighting_to_subject(self, sighting_id, subject_id):

        url = "{0}/{1}/{2}/{3}".format(self.base_url, self.sighting, sighting_id, subject_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="POST")
        r = requests.post(url, headers=self.header)

        if self.verbose:
            print print_http_response(r)

        if r.json()['status'] != 'success':
            print r.text
            # raise Exception("Add sighting to subject failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

    def list_sightings(self, page=1, number_per_page=1000, data={}):
        """
        Get sightings
        :return:
        """
        url = u"{}/{}/{}/{}".format(self.base_url, self.sighting, page, number_per_page)

        sep = "?"
        if data is not None and len(data) > 0:
            for i, v in enumerate(data):
                if data[v] is not None:
                    url += sep + v + "=" + unicode(data[v])
                    sep = "&"

        #print(u"URL {}".format(url))
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET")

        r = requests.get(url, headers=self.header)

        if self.verbose:
            print print_http_response(r)
            # raise Exception("List sightings: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

    def add_description(self, subject_id, description_id):
        pass

    def delete_description(self, description_id):
        url = "{0}/{1}/{2}".format(self.base_url, self.description, description_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="DELETE")
        r = requests.delete(url, headers=self.header)

        if self.verbose:
            print print_http_response(r)

        if r.json()['status'] != 'success':
            print r.text
            # raise Exception("Failed to delete description: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()



    # list all available watchlist
    def list_watchlists(self, ignore_unknown=False):
        url = "{0}/{1}".format(self.base_url, self.watchlist)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET")

        r = requests.get(url, headers=self.header)
        if self.verbose:
            print print_http_response(r)

        json_resp = r.json()
        if json_resp['status'] != 'success':
            print r.text

        if json_resp['status'] == 'success' and ignore_unknown:
            watchlists = []
            for watchlist in json_resp['data']['watchlists']:
                if watchlist['name'] != 'Unknown':
                    watchlists.append(watchlist)
            # return watchlists
            json_resp['data']['watchlists'] = watchlists

        return json_resp

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









