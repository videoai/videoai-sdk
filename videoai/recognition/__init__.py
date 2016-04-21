__author__ = 'kieron'

from videoai import VideoAIUser
import json
import requests

class Recognition(VideoAIUser):

    def __init__(self, host='', key_file = '', api_id='', api_secret='', verbose=False):
        super(Recognition, self).__init__(host=host, key_file=key_file, api_id=api_id, api_secret=api_secret, verbose=verbose)
        self.subject = 'subject'
        self.tag = 'tag'
        self.description = 'description'
        self.detection = 'detection'
        self.sighting = 'sighting'
        pass

    def subject_thumbnail(self, subject_id):
        url = '{}/{}/{}'.format(self.base_url, 'thumbnail/subject', subject_id)
        r = requests.get(url, headers=self.header, allow_redirects=True)
        return r.content

    def description_thumbnail(self, description_id):
        url = '{}/{}/{}'.format(self.base_url, 'thumbnail/description', description_id)
        r = requests.get(url, headers=self.header, allow_redirects=True)
        return r.content

    def detection_thumbnail(self, detection_id):
        url = '{}/{}/{}'.format(self.base_url, 'thumbnail/detection', detection_id)
        r = requests.get(url, headers=self.header, allow_redirects=True)
        return r.content

    def sighting_thumbnail(self, sighting_id):
        url = '{}/{}/{}'.format(self.base_url, 'thumbnail/sighting', sighting_id)
        r = requests.get(url, headers=self.header, allow_redirects=True)
        return r.content

    def sighting_acknowledge(self, sighting_id):
        url = '{}/sighting/{}/acknowledge'.format(self.base_url, sighting_id)
        r = requests.get(url, headers=self.header, allow_redirects=True)
        return r.content

    def sighting_true(self, sighting_id):
        url = '{}/sighting/{}/true'.format(self.base_url, sighting_id)
        r = requests.get(url, headers=self.header, allow_redirects=True)
        return r.content

    def sighting_error(self, sighting_id):
        url = '{}/sighting/{}/error'.format(self.base_url, sighting_id)
        r = requests.get(url, headers=self.header, allow_redirects=True)
        return r.content

    def create_subject(self, name, user_data={}):
        """
        Create a new subject
        :param name: a name to give the subject
        :param user_data: a dictionary of user data, this will get stored as JSON
        :return: subject_id: The subject_id of the created subject
        """
        url = "{0}/{1}".format(self.base_url, self.subject)

        json_user_data = json.dumps(user_data)
        print json_user_data

        data = { 'name': name, 'user_data': json_user_data }

        r = requests.post(url, headers=self.header, data=data, allow_redirects=True)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Create subject failed: {}". format(r.json()['message']))

        subject = r.json()['data']['subject']
        return subject


    def get_subject(self, subject_id):
        """
        Get a subject
        """
        url = "{0}/{1}/{2}".format(self.base_url, self.subject, subject_id)
        print 'URL {}'.format(url)

        r = requests.get(url, headers=self.header, allow_redirects=True)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print 'now here'
            print r.text
            raise Exception("Get subject failed: {}". format(r.json()['message']))

        try:
            s = r.json()['data']['subject']
        except:
            raise Exception("Failed to decode JSON")
        return s


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


    def list_subjects(self, tag_id=''):
        """
        List all the subjects
        :param tag_id: If specified then filter by this tag
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

    def enrol_from_image(self, subject_id, image_file):
        pass

    def add_sighting_to_subject(self, sighting_id, subject_id):

        url = "{0}/{1}/{2}/{3}".format(self.base_url, self.sighting, sighting_id, subject_id)
        print url
        r = requests.post(url, headers=self.header)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Add sighting to subject failed: {}". format(r.json()['message']))

        return True

    def add_detection_to_subject(self, detection_id, subject_id):

        url = "{0}/{1}/{2}/{3}".format(self.base_url, self.detection, detection_id, subject_id)
        print "URL {}".format(url)
        r = requests.post(url, headers=self.header)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Add detection to subject failed: {}". format(r.json()['message']))

        return True

    def list_sightings(self, page=1, number_per_page=1000):
        """
        Get sightings
        :return:
        """

        url = "{0}/{1}".format(self.base_url, self.sighting)

        r = requests.get(url, headers=self.header)

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("List sightings: {}". format(r.json()['message']))

        subjects = r.json()['sightings']
        return subjects

    def add_description(self, subject_id, description_id):
        pass


    def delete_description(self, description_id):
        url = "{0}/{1}/{2}".format(self.base_url, self.description, description_id)
        print url
        r = requests.delete(url, headers=self.header)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Failed to delete description: {}". format(r.json()['message']))

        return True

    def create_tag(self, name):
        url = "{0}/{1}".format(self.base_url, self.tag)

        data = { 'name': name }

        r = requests.post(url, headers=self.header, data=data, allow_redirects=True)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Create tag failed: {}". format(r.json()['message']))

        tag = r.json()['data']['tag']
        return tag

    def delete_tag(self, tag_id):

        url = "{0}/{1}/{2}".format(self.base_url, self.tag, tag_id)

        r = requests.delete(url, headers=self.header)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Delete tag failed: {}". format(r.json()['message']))

        return tag_id

    def list_tags(self):
        url = "{0}/{1}".format(self.base_url, self.tag)

        r = requests.get(url, headers=self.header)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Create subject failed: {}". format(r.json()['message']))

        return r.json()['data']['tags']

    def set_default_tag(self, tag_id):
        pass
