import os
import base64
import requests
import oauth2 as oauth
import time
from os.path import expanduser
from configparser import ConfigParser
import json

SIGN_REQUEST = True


class Error(Exception):
    """Base-class for all exceptions raised by this module"""


class InvalidKeyFile(Error):
    """Invalid key-file"""


def get_parameter(param, name, parser):
    section = 'videoai.net'
    if not param:
        if not parser.has_option(section, name):
            raise InvalidKeyFile('Missing {} parameter.'.format(name))
        return parser.get(section, name)
    return param

def print_http_response(r):
    '''
    Print the http response
    :param r: The response of a request
    :return:
    '''
    print "HTTP/1.0 {} OK".format(r.status_code)
    print "Content-Type: {}".format(r.headers['content-type'])
    print "Content-Length: {}".format(r.headers['content-length'])
    print "Server: {}".format(r.headers['server'])
    print "Date: {}".format(r.headers['date'])
    print r.text


# This function will sign a request using, method, url (with parameters), data (form parameters)
#       if oauth_nonce and oauth_timestamp are not None it will use those provided ==> used to check signature
#       if oauth_nonce and oauth_timestamp are None they will be generated
# and return the header containing signature
def sign_request(url,
                 client_id,
                 client_secret,
                 token='',
                 data=None,
                 method="GET",
                 oauth_nonce=None,
                 oauth_timestamp=None):

    # Set the base oauth_* parameters along with any other parameters required
    # for the API call.
    # url = "{0}/{1}".format(self.base_url, self.end_point)
    # files = {'video': open("{0}".format(video_file))}
    # data = {'algorithm': self.algorithm, 'max_frames':max_frames }

    if oauth_nonce is None:
        oauth_nonce = oauth.generate_nonce()
    if oauth_timestamp is None:
        oauth_timestamp = str(int(time.time()))
    params = {
        'oauth_version': '1.0',
        'oauth_nonce': oauth_nonce,
        'oauth_timestamp': oauth_timestamp
    }
    if data is not None:
        params.update(data)

    # Set up instances of our Token and Consumer. The Consumer.key and
    # Consumer.secret are given to you by the API provider. The Token.key and
    # Token.secret is given to you after a three-legged authentication.
    token = oauth.Token(key=token, secret="")
    consumer = oauth.Consumer(key=client_id, secret=client_secret)

    # Set our token/key parameters
    params['oauth_token'] = token.key
    params['oauth_consumer_key'] = consumer.key

    # Create our request. Change method, etc. accordingly.
    #print("----- Parameters: {}".format(params))
    #print("----- URL {}".format(url))
    #print("----- method {}".format(method))

    req = oauth.Request(method=method.upper(), url=url, parameters=params)

    # Sign the request.
    signature_method = oauth.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, consumer, token)

    return req.to_header()


class VideoAIUser(object):

    def __init__(self, token, host, client_id, client_secret, verbose=False):

        self.base_url = host
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = token
        self.verbose = verbose
        self.end_point = 'task'

        # if the request is not signed token is provided in Authorization header Basic
        if not SIGN_REQUEST:
            formatted_token = "{0}:no_use".format(token)
            basic_auth_header = "Basic {0}".format(formatted_token)
            self.header = {'Authorization': basic_auth_header}

        print ("client_id / client_secret {}/{}".format(self.client_id, self.client_secret))
        print "Using VideoAI host '{}'".format(self.base_url)


    @classmethod
    def create(cls,
               key_file='',
               email='',
               password='',
               client_id='',
               client_secret='',
               authentication_server='',
               verbose=False):
        """Construct from bits and pieces.  Missing parameters get picked up from key_file."""

        # Need some information from the key-file
        if not key_file:
            home = expanduser("~")
            key_file = os.path.join(home, '.videoai')
        parser = ConfigParser()
        parser.read(key_file)

        try:
            email = get_parameter(param=email, name='email', parser=parser)
            password = get_parameter(param=password, name='password', parser=parser)
            client_id = get_parameter(param=client_id, name='client_id', parser=parser)
            client_secret = get_parameter(param=client_secret, name='client_secret', parser=parser)
            authentication_server = get_parameter(param=authentication_server, name='authentication_server',
                                                  parser=parser)
        except:
            raise

        # Next we have
        data = {
            "email": email,
            "password": password
        }

        url = '{}/auth/api_login?client_id={}'.format(authentication_server, client_id)
        header = sign_request(url=url, client_id=client_id, client_secret=client_secret, data=data, method='POST')
        response = requests.post(url, data, headers=header)
        json_response = json.loads(response.text)
        token = json_response['token']['token']
        host = json_response['user']['api_url']

        return cls(token=token, host=host, client_id=client_id, client_secret=client_secret, verbose=verbose)

    # This function will sign a request using, method, url (with parameters), data (form parameters)
    #       if oauth_nonce and oauth_timestamp are not None it will use those provided ==> used to check signature
    #       if oauth_nonce and oauth_timestamp are None they will be generated
    # and return the header containing signature
    def sign_request(self,
                     url,
                     data=None,
                     method="GET",
                     oauth_nonce=None,
                     oauth_timestamp=None):

        self.header = sign_request(url=url,
                                   client_id=self.client_id,
                                   client_secret=self.client_secret,
                                   token=self.token,
                                   data=data,
                                   method=method,
                                   oauth_nonce=oauth_nonce,
                                   oauth_timestamp=oauth_timestamp)

    def wait(self, response):

        task = response['task']

        # now we need to add client_id in the url
        url = "{0}/{1}/{2}?client_id={3}".format(self.base_url, self.end_point, task['job_id'], self.client_id)

        if task['complete']:
            return task

        while not task['complete']:
            time.sleep(0.5)
            if SIGN_REQUEST:
                self.sign_request(url, data=None, method="GET")

            r = requests.get(url, headers=self.header, allow_redirects=True)
            task = r.json()['task']

            if self.verbose:
                print r.json()

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

    def download_file(self, url, local_filename='', local_dir=''):

        if not url:
            print 'Invalid download URL'
            return ''

        if not local_filename:
            local_filename = url.split('/')[-1]

        if local_dir:
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            local_filename = os.path.join(local_dir, local_filename)

        print 'Downloading {0} to {1}'.format(url, local_filename)
        r = requests.get(url, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return local_filename

    def download_with_authentication(self, end_point, local_filename=''):
        if not local_filename:
            local_filename = end_point.split('/')[-1]
        url = '{}{}?client_id={}'.format(self.base_url, end_point, self.client_id)
        print 'Downloading {0} to {1}'.format(url, local_filename)

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET")
        print url

        r = requests.get(url, headers=self.header, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return local_filename

    def authenticate(self):
        '''
        Simply try to authenticate
        :return:
        '''
        url = "{0}/{1}?client_id={2}".format(self.base_url, "handshake", self.client_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET")

        r = requests.get(url, headers=self.header, allow_redirects=True)
        if self.verbose:
            print_http_response(r)
        return r.json()

    def tasks(self, page=1, number_per_page=3):
        '''
        Get a list of all tasks
        :return:
        '''
        url = "{0}/{1}/{2}/{3}?client_id={4}".format(self.base_url, self.end_point, page, number_per_page,
                                                     self.client_id)

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET")

        r = requests.get(url, headers=self.header, allow_redirects=True)
        if self.verbose:
            print_http_response(r)

        return r.json()

        if r.json()['status'] != 'success':
            print r.text
            # raise Exception("List tasks failed: {}".format(r.json()['message']))

        return r.json()

    def task(self, job_id):
        '''
        Get a specific task
        :return:
        '''
        url = "{0}/{1}/{2}?client_id={3}".format(self.base_url, self.end_point, job_id, self.client_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET")

        r = requests.get(url, headers=self.header, allow_redirects=True)

        if self.verbose:
            print_http_response(r)
        return r.json()


class FaceLogImage(VideoAIUser):

    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(FaceLogImage, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                      verbose=verbose)
        self.end_point = 'face_log_image'

    def request(self, image_file, min_size=80, recognition=0, compare_threshold=0.6):

        file_size = os.path.getsize(image_file) / 1000000.0

        data = {'min_size': min_size, 'recognition': recognition, 'compare_threshold': compare_threshold}

        url = "{0}/{1}?client_id={2}".format(self.base_url, self.end_point, self.client_id)

        files = {'image': open("{0}".format(image_file))}
        if SIGN_REQUEST:
            self.sign_request(url, data=data, method="POST")

        try:
            r = requests.post(url, headers=self.header, files=files, data=data, allow_redirects=True)
        except:
            return

        if r.json()['status'] != 'success':
            print print_http_response(r)
            # raise Exception("Face Log request failed: {}". format(r.json()['message']))

        if self.verbose:
            print print_http_response(r)

        return r.json()

    def apply(self, image_file, download=True, min_size=80, recognition=0, compare_threshold=0.5,
              wait_until_finished=True, local_output_dir=''):

        response = self.request(image_file, min_size=min_size, recognition=recognition,
                                compare_threshold=compare_threshold)

        if not wait_until_finished:
            return response

        response = self.wait(response)
        task = response['task']
        if not task['success']:
            print 'Failed FaceLogImage: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['results_image'], local_dir=local_output_dir)
            for sighting in task['sightings']:
                self.download_file(sighting['thumbnail'], local_dir=local_output_dir)
        return task


class FaceLog(VideoAIUser):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(FaceLog, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                      verbose=verbose)
        self.end_point = 'face_log'

    def request(self, video_file, start_frame=0, max_frames=0, min_size=80, recognition=0, compare_threshold=0.6):

        file_size = os.path.getsize(video_file) / 1000000.0
        print 'Requested FaceLog on video {0} ({1} Mb)'.format(video_file, file_size)
        data = {
            'start_frame': start_frame,
            'max_frames': max_frames,
            'recognition': recognition,
            'compare_threshold': compare_threshold,
            'min_size': min_size,
        }

        url = "{0}/{1}?client_id={2}".format(self.base_url, self.end_point, self.client_id)

        files = {'video': open("{0}".format(video_file))}
        if SIGN_REQUEST:
            self.sign_request(url, data=data, method="POST")
        r = requests.post(url, headers=self.header, files=files, data=data, allow_redirects=True)
        if r.json()['status'] != 'success':
            print print_http_response(r)
            raise Exception("face_log request failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

    def apply(self, video_file, download=True, start_frame=0, max_frames=0, min_size=80, recognition=0,
              compare_threshold=0.6, wait_until_finished=True, local_output_dir=''):

        response = self.request(video_file, recognition=recognition, compare_threshold=compare_threshold,
                            start_frame=start_frame, max_frames=max_frames, min_size=min_size)

        if not wait_until_finished:
            return response

        response = self.wait(response)
        task = response['task']
        if not task['success']:
            print 'Failed FaceLog: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['results_video'], local_dir=local_output_dir)

            for sighting in task['sightings']:
                self.download_file(sighting['thumbnail'], local_dir=local_output_dir)
        return response


class FaceAuthenticate(VideoAIUser):

    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(FaceAuthenticate, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                               verbose=verbose)
        self.end_point = 'face_authenticate'

    def request(self, gallery, probe1, probe2='', compare_threshold=0.6):

        file_size = os.path.getsize(gallery) / 1000000.0
        print 'Requested FaceAuthenticate on {0} ({1} Mb)'.format(gallery, file_size)

        data = {'compare_threshold': compare_threshold}

        url = "{0}/{1}?client_id={2}".format(self.base_url, self.end_point, self.client_id)

        files = {
            'gallery': open('{}'.format(gallery))
        }

        if probe1:
            files['probe1'] = open('{}'.format(probe1))

        if probe2:
            files['probe2'] = open('{}'.format(probe2))

        if len(files) < 2:
            raise Exception('Only 1 image file specified')

        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST")
            r = requests.post(url, headers=self.header, files=files, data=data, allow_redirects=True)
        except:
            return

        if r.json()['status'] != 'success':
            print print_http_response(r)
            # raise Exception("Face Authenticate request failed: {}". format(r.json()['message']))

        if self.verbose:
            print print_http_response(r)

        return r.json()


    def apply(self, gallery, probe1='', probe2='', download=True, compare_threshold=0.6, wait_until_finished=True):

        response = self.request(gallery=gallery, probe1=probe1, probe2=probe2, compare_threshold=compare_threshold)

        if not wait_until_finished:
            return response

        response = self.wait(response)

        task = response['task']
        if not task['success']:
            print 'Failed FaceLogImage: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['gallery_thumbnail'])
            self.download_file(task['probe1_thumbnail'])
            if task['probe2_thumbnail']:
                self.download_file(task['probe2_thumbnail'])
        return task




