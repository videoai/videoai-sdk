__author__ = 'kieron'

from videoai import VideoAIUser
import json
import requests

class Recognition(VideoAIUser):

    def __init__(self, host='', key_file = '', api_id='', api_secret='', verbose=False):
        super(Recognition, self).__init__(host=host, key_file=key_file, api_id=api_id, api_secret=api_secret, verbose=verbose)
        self.subject = 'subject'
        self.tag = 'tag'
        self.tagged = 'tagged'
        self.description = 'description'
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

    def create_subject(self, name, tag='', tag_data='', user_data={'gender':'Unknown', 'notes':''}):
        """
        Create a new subject
        :param name: a name to give the subject
        :param user_data: a dictionary of user data, this will get stored as JSON
        :param tag: a single tag to add and associate to the created subject
        :param tag_data: a dictionary of tag, this will get stored as JSON
        :return: subject_id: The subject_id of the created subject
        """
        url = "{0}/{1}".format(self.base_url, self.subject)

        json_user_data = json.dumps(user_data)

        data = { 'name': name, 'user_data': json_user_data }

        # if we have a valid tag-id then we try and use it
        if tag:
            data['tag'] = tag

        if tag_data:
            data['tag_data'] = json.dumps(tag_data)

        print ("data {}".format(data))
        r = requests.post(url, headers=self.header, data=data, allow_redirects=True)

        if r.json()['status'] != 'success':
            raise Exception("Create subject failed: {}". format(r.json()['message']))

        subject = r.json()['data']['subject']
        return subject

    def edit_subject(self, subject_id, name='', tag_data_to_add='', tag_data_to_remove='', user_data={}):
        """
        Edit an existing subject
        """
        url = "{0}/{1}/{2}".format(self.base_url, self.subject, subject_id)
        print "USING URL {}".format(url) 
        data = {}

        if name:
            data['name'] = name

        if user_data:
            data['user_data'] = json.dumps(user_data)
        
        if tag_data_to_add:
            data['tag_data_to_add'] = tag_data_to_add

        if tag_data_to_remove:
            data['tag_data_to_remove'] = tag_data_to_remove

        r = requests.put(url, headers=self.header, data=data, allow_redirects=True)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Edit subject failed: {}". format(r.json()['message']))

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

    # Returns job_id if task has been successfully launched
    # raise an error instead
    def add_sighting_to_subject(self, sighting_id, subject_id):

        url = "{0}/{1}/{2}/{3}".format(self.base_url, self.sighting, sighting_id, subject_id)
        print url
        r = requests.post(url, headers=self.header)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Add sighting to subject failed: {}". format(r.json()['message']))

        try:
            s = r.json()['task']
        except:
            raise Exception("Failed to decode JSON")
        return s

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

    def create_tag(self, name, colour='', sound=''):

        url = "{0}/{1}/{2}".format(self.base_url, self.tag, name)
        print url
        data = {}
        if colour:
            data['colour'] = colour
        if sound:
            data['sound'] = sound

        r = requests.post(url, headers=self.header, data=data, allow_redirects=True)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Update tag failed: {}". format(r.json()['message']))

        return True

    # Create or update a tag for an object
    def tag_object(self, name, object_id, new_name=''):

        if not object_id:
            raise Exception("Tag object failed.  No object_id specified")
        if not new_name:
            url = "{0}/{1}/{2}/{3}".format(self.base_url, self.tagged, name, object_id)
        else:
            url = "{0}/{1}/{2}/{3}/{4}".format(self.base_url, self.tagged, name, object_id, new_name)

        print 'URI: {}'.format(url)

        r = requests.post(url, headers=self.header, allow_redirects=True)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Update tag failed: {}". format(r.json()['message']))

        return True

    # Delete all tags
    def delete_tag(self, tag_name='', object_id=''):
        print 'Deleting {} {}'.format(tag_name, object_id)
        if not tag_name and not object_id:
            url = "{0}/{1}/{2}".format(self.base_url, self.tag, tag_name)
        elif tag_name and not object_id:     
            url = "{0}/{1}/{2}".format(self.base_url, self.tag, tag_name)
        elif not tag_name and object_id:     
            url = "{0}/object/{1}".format(self.base_url, object_id)
        elif tag_name and object_id:
            url = "{0}/{1}/{2}/{3}".format(self.base_url, self.tag, tag_name, object_id)
        else:
            print 'Trouble in input parameters'
            return False

        r = requests.delete(url, headers=self.header)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Delete tag failed: {}". format(r.json()['message']))

        return True 
   
    # list all available tags
    def list_tags(self, ignore_unknown=False):

        # Get every object and every tag
        url = "{0}/{1}".format(self.base_url, self.tag)
        
        r = requests.get(url, headers=self.header)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("List tags failed: {}". format(r.json()['message']))

        if ignore_unknown:
            tags = []
            for tag in r.json()['data']['tags']:
                if tag['name'] != 'Unknown':
                    tags.append(tag)
            return tags

        return r.json()['data']['tags']

    def default_tags(self):
        tags = [] 
        for tag in self.list_tags():
            tags.append(tag['name'])

        if 'Unknown' not in tags:
            self.create_tag('Unknown', '#95a5a6')
        if 'Staff' not in tags:
            self.create_tag('Staff', '#3498db')
        if 'Contractor' not in tags:
            self.create_tag('Contractor', '#9b59b6')
        if 'Visitor' not in tags:
            self.create_tag('Visitor', '#e67e22')
        if 'High Risk' not in tags:
            self.create_tag('High Risk', '#e74c3c')
        return self.list_tags(ignore_unknown=True) 

    # list all tags, tags for object, or objects with tag
    def list_tagged(self, tag_name='', object_id=''):

        # Get every object and every tag
        if tag_name and object_id:
            url = "{0}/{1}/{2}/{3}".format(self.base_url, self.tagged, tag_name, object_id)
        # Get all objects with a particular tag
        elif not object_id and tag_name:
            url = "{0}/{1}/{2}".format(self.base_url, self.tagged, tag_name)
        # Get all tags for a particular object
        elif object_id and not tag_name :
            url = "{0}/object/{2}".format(self.base_url, self.tagged, object_id)
        else:
            url = "{0}/{1}".format(self.base_url, self.tagged)
        
        print url

        r = requests.get(url, headers=self.header)
        print r.text
        print r.status_code

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("List tags failed: {}". format(r.json()['message']))

        return r.json()['data']['tags']




