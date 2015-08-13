__author__ = 'kieron'

from videoai import VideoAIUser
import json
import requests

class Recognition(VideoAIUser):

    def __init__(self, key_file='', verbose=True):
        super(Recognition, self).__init__(key_file=key_file, verbose=verbose)
        self.subject = 'subject'
        self.watchlist = 'watchlist'
        self.description = 'description'
        pass

    def create_subject(self, name, user_data):
        """
        Create a new subject
        :param name: a name to give the subject
        :param user_data: a dictionary of user data, this will get stored as JSON
        :return:
        """
        url = "{0}/{1}".format(self.base_url, self.subject)

        json_user_data = json.dumps(user_data)
        print json_user_data

        data = { 'name': name }

        r = requests.post(url, headers=self.header, data=data, allow_redirects=True)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Create subject failed: {}". format(r.json()['message']))

        subject = r.json()['data']['subject']
        return subject



    def delete_subject(self, subject_id):
        """
        Delete a subject
        :param subject_id: The subject id
        :return:
        """
        url = "{0}/{1}/{2}".format(self.base_url, self.subject, subject_id)

        r = requests.delete(url, headers=self.header)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Deleted subject failed: {}". format(r.json()['message']))

        return subject_id


    def list_subjects(self, watchlist_id=''):
        """
        List all the subjects
        :param watchlist_id: If specified then filter by this watchlist
        :return:
        """

        url = "{0}/{1}".format(self.base_url, self.subject)

        r = requests.get(url, headers=self.header)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Create subject failed: {}". format(r.json()['message']))

        subjects = r.json()['data']['subjects']
        return subjects

    def enrol_from_image(self, subject_id, image_file, watchlist_id=''):
        pass

    def add_from_sighting(self, subject_id, sighting_id, watchlist_id=''):
        pass

    def add_description(self, subject_id, description_id, watchlist_id=''):
        pass

    def delete_description(self, description_id):
        pass

    def create_watchlist(self, name):
        url = "{0}/{1}".format(self.base_url, self.watchlist)

        data = { 'name': name }

        r = requests.post(url, headers=self.header, data=data, allow_redirects=True)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Create watchlist failed: {}". format(r.json()['message']))

        watchlist = r.json()['data']['watchlist']
        return watchlist

    def delete_watchlist(self, watchlist_id):

        url = "{0}/{1}/{2}".format(self.base_url, self.watchlist, watchlist_id)

        r = requests.delete(url, headers=self.header)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Delete watchlist failed: {}". format(r.json()['message']))

        return watchlist_id

    def list_watchlists(self):
        url = "{0}/{1}".format(self.base_url, self.watchlist)

        r = requests.get(url, headers=self.header)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Create subject failed: {}". format(r.json()['message']))

        return r.json()['data']['watchlists']

    def set_default_watchlist(self, watchlist_id):
        pass
