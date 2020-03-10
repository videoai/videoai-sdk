import os
import base64
import requests
import oauth2 as oauth
import time
from os.path import expanduser
from configparser import ConfigParser
import json
import socket
from urlparse import urlsplit
import pkg_resources

# import logging
# logger = logging.getLogger(__name__)

# import logging.config
# config_file = '/home/anegri/__Development__/VideoAI.net/sdk/videoai/logging_config.ini'
# logging.config.fileConfig(config_file)

# from logger import console_logger, file_logger
# if False:
#    console_logger.debug('debug message')
#    console_logger.info('info message')
#    console_logger.warn('warn message')
#    console_logger.error('error message')
#    console_logger.critical('critical message')

#    file_logger.debug('debug message in File')
#    file_logger.info('info message in File')
#    file_logger.warn('warn message in File')
#    file_logger.error('error message in File')
#    file_logger.critical('critical message in File')

VERIFY_SSL = False
SIGN_REQUEST = True

LOCALISE_IP_ADDRESS = False


class Version():
    @staticmethod
    def get_version():
        version = "undef"
        try:
            version = pkg_resources.get_distribution('videoai-sdk').version
        except Exception as e:
            print("Unable to get version from package")
        return version


class Error(Exception):
    """Base-class for all exceptions raised by this module"""


class InvalidKeyFile(Error):
    """Invalid key-file"""


class FailedAPICall(Error):
    """Failed to call an API function"""


class AuthenticationError(Error):
    """Failed to be authenticated"""


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
    if 'server' in r.headers:
        print "Server: {}".format(r.headers['server'])
    if 'date' in r.headers:
        print "Date: {}".format(r.headers['date'])
    print json.dumps(r.json(), indent=4, sort_keys=True)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


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
                 oauth_timestamp=None,
                 request=None):
    # console_logger.info("in sign !!!!@!@!@!@!@!")
    # Set the base oauth_* parameters along with any other parameters required
    # for the API call.
    # url = "{0}/{1}".format(self.base_url, self.end_point)
    # files = {'video': open("{0}".format(video_file))}
    # data = {'algorithm': self.algorithm, 'max_frames':max_frames }
    initial_user_agent = ""
    if request is not None:
        initial_user_agent = "user_agent={}".format(request.user_agent).replace(',', ';')
    if oauth_nonce is None:
        oauth_nonce = oauth.generate_nonce()
    if oauth_timestamp is None:
        oauth_timestamp = str(int(time.time()))

    device_data = ""
    if request is not None:
        ip_addr = None
        try:
            ip_addr = request.remote_addr
            # Convert IPv6 to IPv4 notation
            if ip_addr[:7] == "::ffff:":
                ip_addr = ip_addr[7:]
        except:
            ip_addr = 'unknown'
    else:
        ip_addr = get_ip()

    lat = None
    lng = None
    if LOCALISE_IP_ADDRESS:
        send_url = 'http://freegeoip.net/json/{}'.format(ip_addr)
        r = requests.get(send_url)
        j = json.loads(r.text)
        lat = j['latitude']
        lng = j['longitude']
    device_data = 'device_id="{}", lat="{}", lng="{}"'.format(ip_addr, lat, lng)

    params = {
        'oauth_version': '1.0',
        'oauth_nonce': str(oauth_nonce),
        'oauth_timestamp': str(oauth_timestamp)
    }
    if device_data is not None and device_data != "":
        params['device_data'] = device_data
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
    # print("----- Parameters: {}".format(params))
    # print("----- URL {}".format(url))
    # print("----- method {}".format(method))

    scheme, netloc, path, query, fragment = urlsplit(url)

    req = oauth.Request(method=method.upper(), url=url, parameters=params)
    # this is a way to avoid checking the base url.
    # we force the normalized_url to only contains endpoint
    req.normalized_url = path

    # Sign the request.
    signature_method = oauth.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, consumer, token)

    header = req.to_header()
    header['Device'] = '{}'.format(device_data)
    header['Initial-User-Agent'] = initial_user_agent
    return header


class VideoAIUser(object):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        # print("host {}".format(host))
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

            #        print ("client_id / client_secret {}/{}".format(self.client_id, self.client_secret))
            #        print "Using VideoAI host '{}'".format(self.base_url)

    @classmethod
    def create(cls,
               key_file='',
               email='',
               password='',
               client_id='',
               client_secret='',
               authentication_server='',
               verbose=False, request=None):
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
        header = sign_request(url=url, client_id=client_id, client_secret=client_secret, data=data, method='POST',
                              request=request)
        response = requests.post(url, data, headers=header, verify=VERIFY_SSL)
        json_response = json.loads(response.text)

        if 'status' in json_response and json_response['status'] == 'fail':
            raise AuthenticationError(json_response['message'])
        token = json_response['oauth_token']['token']
        host = json_response['user']['api_url']
        try:
            port_number = int(host)
            host = json_response['user']['internal_api_url']
        except Exception as e:
            pass

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
                     oauth_timestamp=None,
                     request=None):

        self.header = sign_request(url=url,
                                   client_id=self.client_id,
                                   client_secret=self.client_secret,
                                   token=self.token,
                                   data=data,
                                   method=method,
                                   oauth_nonce=oauth_nonce,
                                   oauth_timestamp=oauth_timestamp,
                                   request=request)

    def create_users_for_unittest(self, users, request=None):
        '''
        Initialize unittest on authentication database
        :return:
        '''
        # Need some information from the key-file
        key_file = ''
        if not key_file:
            home = expanduser("~")
            key_file = os.path.join(home, '.videoai')
        parser = ConfigParser()
        parser.read(key_file)

        try:
            authentication_server = get_parameter(param=None, name='authentication_server',
                                                  parser=parser)
        except:
            raise
        data = {'users': json.dumps(users)}
        url = '{}/auth/initialize_unittest'.format(authentication_server)
        self.sign_request(url=url, data=data, method='POST', request=request)
        response = requests.post(url, data, headers=self.header, verify=VERIFY_SSL)
        if response.status_code == 200:
            return True, response.content, response.headers
        else:
            return False, None, None

    def finalize_unittest(self, request=None):
        '''
        Initialize unittest on authentication database
        :return:
        '''
        # Need some information from the key-file
        key_file = ''
        if not key_file:
            home = expanduser("~")
            key_file = os.path.join(home, '.videoai')
        parser = ConfigParser()
        parser.read(key_file)

        try:
            client_id = get_parameter(param=None, name='client_id', parser=parser)
            client_secret = get_parameter(param=None, name='client_secret', parser=parser)
            authentication_server = get_parameter(param=None, name='authentication_server',
                                                  parser=parser)
        except:
            raise

        url = '{}/auth/finalize_unittest'.format(authentication_server)
        self.sign_request(url=url, data=None, method='POST', request=request)
        response = requests.post(url, None, headers=self.header, verify=VERIFY_SSL)
        json_response = json.loads(response.text)
        if self.verbose:
            print print_http_response(response)

        if response.status_code == 200:
            return True, response.content, response.headers
        else:
            return False, None, None

    def wait(self, response, request=None):

        task = response['task']

        # endpoint is selected by the task analytics itself
        # using face_log_stream we are creating sub task that are face_log_image.
        # using class endpoint is not enough,
        # as wait for apply in face_log_stream is not for waiting on the face_log_stream task
        # but on the subtask on face_log_image
        url = "{0}/{1}/{2}".format(self.base_url, task['analytic'], task['job_id'])

        if task['complete']:
            return task

        while not task['complete']:
            time.sleep(0.5)
            if SIGN_REQUEST:
                self.sign_request(url, data=None, method="GET", request=request)

            r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
            json_data = r.json()
            if self.verbose:
                print json.dumps(json_data, indent=4, sort_keys=True)
            task = json_data['task']

        return json_data

    def download_file(self, url, local_filename='', local_dir='', request=None):

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
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)
        r = requests.get(url, headers=self.header, stream=True, verify=VERIFY_SSL)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return local_filename

    def download_with_authentication(self, end_point, local_filename='', request=None):
        if not local_filename:
            local_filename = end_point.split('/')[-1]
        url = '{}{}'.format(self.base_url, end_point)
        print 'Downloading {0} to {1}'.format(url, local_filename)

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

        r = requests.get(url, headers=self.header, stream=True, verify=VERIFY_SSL)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return local_filename

    def authenticate(self, request=None):
        '''
        Simply try to authenticate
        :return:
        '''
        url = "{0}/{1}".format(self.base_url, "handshake")
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
        if self.verbose:
            print_http_response(r)
        return r.json()

    def import_tasks_report(self, job_id, page=1, number_per_page=3, show_ignored=False, request=None):
        '''
        Get a list of all tasks or if job_id provided of all subtask of job_id
        :return:
        '''

        url = "{0}/subtasks/{1}/{2}/{3}".format(self.base_url, job_id, page, number_per_page)
        url += "?show_ignored={}".format(show_ignored)

        if SIGN_REQUEST:
            self.sign_request(url, method="GET", request=request)

        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
        if self.verbose:
            print_http_response(r)

        return r.json()

    def tasks(self, page=1, number_per_page=3, search_by_category="", request=None):
        '''
        Get a list of all tasks
        :return:
        '''

        url = "{0}/{1}/{2}/{3}?search_by_category={4}".format(self.base_url, self.end_point, page, number_per_page,
                                                              search_by_category)

        if SIGN_REQUEST:
            self.sign_request(url, method="GET", request=request)

        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
        if self.verbose:
            print_http_response(r)

        return r.json()

    def task(self, job_id, request=None):
        '''
        Get a specific task
        :return:
        '''
        url = "{0}/{1}/{2}".format(self.base_url, self.end_point, job_id)

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
        if self.verbose:
            print_http_response(r)

        return r.json()

    def source_file(self, job_id, request=None):
        '''
        Get source file of a job from a job_id
        :return:
        '''
        url = "{}/source_file/{}".format(self.base_url, job_id)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)

        if self.verbose:
            print print_http_response(r)

        if r.status_code == 200:
            return True, r.content, r.headers
        else:
            return False, None, None

    def result_file(self, domain_id, day_count, job_id, filename, request=None):
        '''
        Get a result file
        :return:
        '''
        url = "{}/results/{}/{}/{}/{}".format(self.base_url, domain_id, day_count, job_id, filename)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)

        if self.verbose:
            print print_http_response(r)

        if r.status_code == 200:
            return True, r.content, r.headers
        else:
            return False, None, None


class VideoAIClient(VideoAIUser):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(VideoAIClient, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                            verbose=verbose)
        self.end_point = 'client'

    def get_data(self, client_id, request=None):

        url = "{0}/{1}/{2}".format(self.base_url, self.end_point, client_id)
        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=None, method="GET", request=request)

            r = requests.get(url,
                             headers=self.header,
                             allow_redirects=True,
                             verify=VERIFY_SSL)

            json_data = r.json()

            if self.verbose:
                print print_http_response(r)

            if json_data['status'] != 'success':
                raise FailedAPICall("Client Get request failed: {}".format(json_data['message']))

        except:
            raise FailedAPICall("Failed to call FaceLogStream:get")

        return json_data

    def request(self):
        pass

    def apply(self):
        pass


class FaceLiveService(VideoAIUser):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(FaceLiveService, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                              verbose=verbose)
        self.end_point = 'face_live_service'

    def request(self):
        pass

    def apply(self):
        pass


class FaceLogStream(VideoAIUser):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(FaceLogStream, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                            verbose=verbose)
        self.end_point = 'face_log_stream'

    def create_stream(self, request=None):
        url = "{0}/{1}".format(self.base_url, self.end_point)

        data = None

        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)

            r = requests.post(url,
                              headers=self.header,
                              data=data,
                              allow_redirects=True,
                              verify=VERIFY_SSL)

            json_data = r.json()

            if self.verbose:
                print print_http_response(r)

            if json_data['status'] != 'success':
                raise FailedAPICall("Face Log Stream Create request failed: {}".format(json_data['message']))

        except:
            raise FailedAPICall("Failed to call FaceLogStream:create")

        return json_data

    def get_result(self, job_id, request=None):
        url = "{0}/{1}/{2}".format(self.base_url, self.end_point, job_id)

        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=None, method="GET", request=request)

            r = requests.get(url,
                             headers=self.header,
                             allow_redirects=True,
                             verify=VERIFY_SSL)

            json_data = r.json()

            if self.verbose:
                print print_http_response(r)

            if json_data['status'] != 'success':
                raise FailedAPICall("Face Log Stream Get request failed: {}".format(json_data['message']))

        except:
            raise FailedAPICall("Failed to call FaceLogStream:get")

        return json_data

    def close_stream(self, job_id, request=None):
        url = "{0}/{1}/{2}/close".format(self.base_url, self.end_point, job_id)

        data = None

        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)

            r = requests.post(url,
                              headers=self.header,
                              data=data,
                              allow_redirects=True,
                              verify=VERIFY_SSL)

            json_data = r.json()

            if self.verbose:
                print print_http_response(r)

            if json_data['status'] != 'success':
                raise FailedAPICall("Face Log Stream Finalize request failed: {}".format(json_data['message']))

        except:
            raise FailedAPICall("Failed to call FaceLogStream:finalize")

        return json_data

    def request(self, image_file, job_id=None, min_size=80, recognition=0, compare_threshold=0.6, top_n=1,
                subject_id='', location=None, request=None):
        '''
        If job_id is None
            that means we are creating the stream
        else
            that means we are adding images to the stream
        '''
        # file_size = os.path.getsize(image_file) / 1000000.0

        data = {
            'min_size': min_size,
            'recognition': recognition,
            'compare_threshold': compare_threshold,
            'top_n': top_n
        }

        if location is not None:
            data['location'] = location

        # are we requested a verification?
        if subject_id is not None:
            data['subject_id'] = subject_id

        url = "{0}/{1}".format(self.base_url, self.end_point)
        if job_id is not None:
            url += "/" + job_id

        files = {'image': open("{0}".format(image_file), mode='rb')}

        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)

            r = requests.post(url,
                              headers=self.header,
                              files=files,
                              data=data,
                              allow_redirects=True,
                              verify=VERIFY_SSL)

            json_data = r.json()

            if self.verbose:
                print print_http_response(r)

            if json_data['status'] != 'success':
                raise FailedAPICall("Face Log Stream request failed: {}".format(json_data['message']))

        except:
            raise FailedAPICall("Failed to call FaceLogStream")

        return json_data

    def apply(self, image_file, job_id=None, download=True, min_size=80, recognition=0, compare_threshold=0.6, top_n=1,
              subject_id='',
              wait_until_finished=True, local_output_dir='', location=None, request=None):
        json_data = self.request(image_file,
                                 job_id=job_id,
                                 min_size=min_size,
                                 recognition=recognition,
                                 compare_threshold=compare_threshold,
                                 top_n=top_n,
                                 subject_id=subject_id,
                                 location=location,
                                 request=request)

        if not wait_until_finished:
            return json_data

        json_data = self.wait(json_data)
        task = json_data['task']
        if not task['success']:
            print 'Failed FaceLogImage: {0}'.format(task['message'])
            return json_data

        if download:
            for sighting in task['sightings']:
                self.download_file(sighting['thumbnail'], local_dir=local_output_dir)
        return json_data


class FaceLogImage(VideoAIUser):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(FaceLogImage, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                           verbose=verbose)
        self.end_point = 'face_log_image'

    def request(self, image_file, min_size=80, recognition=0, compare_threshold=0.6, top_n=1, subject_id='',
                location=None, request=None):

        file_size = os.path.getsize(image_file) / 1000000.0

        data = {
            'min_size': min_size,
            'recognition': recognition,
            'compare_threshold': compare_threshold,
            'top_n': top_n
        }

        if location is not None:
            data['location'] = location

        # are we requested a verification?
        if subject_id is not None:
            data['subject_id'] = subject_id

        url = "{0}/{1}".format(self.base_url, self.end_point)

        files = {'image': open("{0}".format(image_file), mode='rb')}

        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)

            r = requests.post(url,
                              headers=self.header,
                              files=files,
                              data=data,
                              allow_redirects=True,
                              verify=VERIFY_SSL)

            json_data = r.json()

            if self.verbose:
                print print_http_response(r)

            if json_data['status'] != 'success':
                raise FailedAPICall("Face Log request failed: {}".format(json_data['message']))

        except:
            raise FailedAPICall("Failed to call FaceLogImage")

        return json_data

    def apply(self, image_file, download=True, min_size=80, recognition=0, compare_threshold=0.6, top_n=1,
              subject_id='',
              wait_until_finished=True, local_output_dir='', location=None, request=None):
        json_data = self.request(image_file,
                                 min_size=min_size,
                                 recognition=recognition,
                                 compare_threshold=compare_threshold,
                                 top_n=top_n,
                                 subject_id=subject_id,
                                 location=location,
                                 request=request)

        if not wait_until_finished:
            return json_data

        json_data = self.wait(json_data)

        task = json_data['task']
        if not task['success']:
            print 'Failed FaceLogImage: {0}'.format(task['message'])
            return json_data

        if download:
            for sighting in task['sightings']:
                self.download_file(sighting['thumbnail'], local_dir=local_output_dir)
        return json_data


class FaceLog(VideoAIUser):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(FaceLog, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                      verbose=verbose)
        self.end_point = 'face_log'

    def request(self, video_file,
                start_frame=0,
                max_frames=0,
                min_size=80,
                recognition=0,
                compare_threshold=0.55,
                top_n=1,
                subject_id=None,
                location=None,
                request=None):

        file_size = os.path.getsize(video_file) / 1000000.0
        print 'Requested FaceLog on video {0} ({1} Mb)'.format(video_file, file_size)
        data = {
            'start_frame': start_frame,
            'max_frames': max_frames,
            'min_size': min_size,
            'recognition': recognition,
            'compare_threshold': compare_threshold,
            'top_n': top_n,
        }

        if location is not None:
            data['location'] = location

        # are we requested a verification?
        if subject_id is not None:
            data['subject_id'] = subject_id

        url = "{0}/{1}".format(self.base_url, self.end_point)

        files = {'video': open("{0}".format(video_file), mode='rb')}
        try:

            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)

            r = requests.post(url,
                              headers=self.header,
                              files=files,
                              data=data,
                              allow_redirects=True,
                              verify=VERIFY_SSL)

            json_data = r.json()

            if self.verbose:
                print print_http_response(r)

            if json_data['status'] != 'success':
                raise FailedAPICall("face_log request failed: {}".format(r.json()['message']))

        except:
            raise FailedAPICall("Failed to run FaceLog")
        return json_data

    def apply(self,
              video_file,
              download=True,
              start_frame=0,
              max_frames=0,
              min_size=80,
              recognition=0,
              compare_threshold=0.6,
              top_n=1,
              subject_id=None,
              wait_until_finished=True,
              local_output_dir='', location=None,
              request=None):

        json_data = self.request(video_file,
                                 recognition=recognition,
                                 compare_threshold=compare_threshold,
                                 top_n=top_n,
                                 start_frame=start_frame,
                                 max_frames=max_frames,
                                 min_size=min_size,
                                 subject_id=subject_id,
                                 location=location,
                                 request=request)

        if not wait_until_finished:
            return json_data

        json_data = self.wait(json_data)
        task = json_data['task']
        if not task['success']:
            print 'Failed FaceLog: {0}'.format(task['message'])
            return json_data

        if download:
            for sighting in task['sightings']:
                self.download_file(sighting['thumbnail'], local_dir=local_output_dir)

        return json_data


class FaceAuthenticate(VideoAIUser):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(FaceAuthenticate, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                               verbose=verbose)
        self.end_point = 'face_authenticate'

    def request(self, gallery, probe1, probe2='', compare_threshold=0.6, request=None):

        file_size = os.path.getsize(gallery) / 1000000.0
        print 'Requested FaceAuthenticate on {0} ({1} Mb)'.format(gallery, file_size)

        data = {'compare_threshold': compare_threshold}

        url = "{0}/{1}".format(self.base_url, self.end_point)

        files = {
            'gallery': open('{}'.format(gallery), mode='rb')
        }

        if probe1:
            files['probe1'] = open('{}'.format(probe1), mode='rb')

        if probe2:
            files['probe2'] = open('{}'.format(probe2), mode='rb')

        if len(files) < 2:
            raise FailedAPICall('Only 1 image file specified')

        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)
            r = requests.post(url, headers=self.header, files=files, data=data, allow_redirects=True, verify=VERIFY_SSL)
            json_data = r.json()
        except:
            raise FailedAPICall('FaceAuthenticate')

        if self.verbose:
            print print_http_response(r)

        if json_data['status'] != 'success':
            raise FailedAPICall("Face Authenticate request failed: {}".format(r.json()['message']))

        return json_data

    def apply(self, gallery, probe1='', probe2='', download=True, compare_threshold=0.6, wait_until_finished=True,
              request=None):

        json_data = self.request(gallery=gallery, probe1=probe1, probe2=probe2, compare_threshold=compare_threshold,
                                 request=request)

        if not wait_until_finished:
            return json_data

        json_data = self.wait(json_data)

        task = json_data['task']
        if not task['success']:
            print 'Failed FaceLogImage: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['gallery_thumbnail'])
            self.download_file(task['probe1_thumbnail'])
            if task['probe2_thumbnail']:
                self.download_file(task['probe2_thumbnail'])
        return task


class BuildVideo(VideoAIUser):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(BuildVideo, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                         verbose=verbose)
        self.end_point = 'build_video'

    def request(self, sighting_id=None, face_log_id=None, request=None):

        print 'Requested Build Video'

        if sighting_id is not None:
            data = {'sighting_id': sighting_id}
        else:
            data = {'face_log_job_id': face_log_id}

        url = "{0}/{1}".format(self.base_url, self.end_point)

        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)
            r = requests.post(url,
                              headers=self.header,
                              data=data,
                              allow_redirects=True, verify=VERIFY_SSL)
            json_data = r.json()
        except:
            raise FailedAPICall('BuildVideo')

        if self.verbose:
            print print_http_response(r)

        if json_data['status'] != 'success':
            raise FailedAPICall("BuildVideo request failed: {}".format(r.json()['message']))

        return json_data

    def from_sighting(self, sighting_id, download=True, wait_until_finished=True):

        json_data = self.request(sighting_id=sighting_id)

        if not wait_until_finished:
            return json_data

        json_data = self.wait(json_data)

        task = json_data['task']
        if not task['success']:
            print 'Failed BuildVideo: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['video'])
        return task

    def from_face_log(self, face_log_id, download=True, wait_until_finished=True, request=None):

        json_data = self.request(face_log_id=face_log_id, request=request)

        if not wait_until_finished:
            return json_data

        json_data = self.wait(json_data)

        task = json_data['task']
        if not task['success']:
            print 'Failed BuildVideo: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['video'])

        return task


class BuildImage(VideoAIUser):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(BuildImage, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                         verbose=verbose)
        self.end_point = 'build_image'

    def request(self, sighting_id=None, face_log_image_id=None, request=None):

        print 'Requested Build Image'

        if sighting_id is not None:
            data = {'sighting_id': sighting_id}
        else:
            data = {'face_log_job_id': face_log_image_id}

        url = "{0}/{1}".format(self.base_url, self.end_point)

        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)
            r = requests.post(url,
                              headers=self.header,
                              data=data,
                              allow_redirects=True, verify=VERIFY_SSL)
            json_data = r.json()
        except:
            raise FailedAPICall('BuildImage')

        if self.verbose:
            print print_http_response(r)

        if json_data['status'] != 'success':
            raise FailedAPICall("BuildImage request failed: {}".format(r.json()['message']))

        return json_data

    def from_sighting(self, sighting_id, download=True, wait_until_finished=True, request=None):

        json_data = self.request(sighting_id=sighting_id, request=request)

        if not wait_until_finished:
            return json_data

        json_data = self.wait(json_data)

        task = json_data['task']
        if not task['success']:
            print 'Failed BuildImage: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['image'])
        return task

    def from_face_log_image(self, face_log_image_id, download=True, wait_until_finished=True, request=None):

        json_data = self.request(face_log_image_id=face_log_image_id, request=request)

        if not wait_until_finished:
            return json_data

        json_data = self.wait(json_data)

        task = json_data['task']
        if not task['success']:
            print 'Failed BuildImage: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['image'])

        return task


class DeleteSubjects(VideoAIUser):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(DeleteSubjects, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                             verbose=verbose)
        self.end_point = 'delete_filtered_subjects'

    def request(self, request=None):

        print 'Requested delete subjects'

        url = "{0}/{1}".format(self.base_url, self.end_point)

        try:
            if SIGN_REQUEST:
                self.sign_request(url, method="POST", request=request)

            r = requests.post(url,
                              headers=self.header,
                              allow_redirects=True,
                              verify=VERIFY_SSL)

            json_data = r.json()

        except:
            raise FailedAPICall('DeleteSubjects')

        if self.verbose:
            print print_http_response(r)

        if json_data['status'] != 'success':
            raise FailedAPICall("DeleteSubjects request failed: {}".format(r.json()['message']))

        return json_data

    def delete_filtered_subjects(self, data, request=None):
        url = "{}/delete_filtered_subjects".format(self.base_url)

        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)

            r = requests.post(url,
                              headers=self.header,
                              data=data,
                              allow_redirects=True,
                              verify=VERIFY_SSL)

            json_data = r.json()

            if self.verbose:
                print print_http_response(r)

            if json_data['status'] != 'success':
                raise FailedAPICall("Error while deleting subjects: {}".format(json_data['message']))

        except:
            raise FailedAPICall("Failed to call delete_filtered_subjects")

        return json_data

    def get_delete_filtered_subjects_task(self, job_id, request=None):
        url = "{}/delete_filtered_subjects/{}".format(self.base_url, job_id)
        data = None
        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="GET", request=request)

            r = requests.get(url,
                             headers=self.header,
                             data=data,
                             allow_redirects=True,
                             verify=VERIFY_SSL)

            json_data = r.json()

            if self.verbose:
                print print_http_response(r)

            if json_data['status'] != 'success':
                raise FailedAPICall("Error while deleting subjects: {}".format(json_data['message']))

        except:
            raise FailedAPICall("Failed to call delete_filtered_subjects")

        return json_data

    def confirm_delete_filtered_subjects_task(self, job_id, request=None):
        url = "{}/delete_filtered_subjects/{}".format(self.base_url, job_id)
        data = None
        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)

            r = requests.post(url,
                              headers=self.header,
                              data=data,
                              allow_redirects=True,
                              verify=VERIFY_SSL)

            json_data = r.json()

            if self.verbose:
                print print_http_response(r)

            if json_data['status'] != 'success':
                raise FailedAPICall("Error while deleting subjects: {}".format(json_data['message']))

        except:
            raise FailedAPICall("Failed to call delete_filtered_subjects")

        return json_data

    def get_subjects_from_deletion_task(self, job_id, page=1, number_per_page=10, request=None):
        url = "{}/subjects_from_deletion_task/{}/{}/{}".format(self.base_url, job_id, page, number_per_page)
        data = None
        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="GET", request=request)

            r = requests.get(url,
                             headers=self.header,
                             data=data,
                             allow_redirects=True,
                             verify=VERIFY_SSL)

            json_data = r.json()

            if self.verbose:
                print print_http_response(r)

            if json_data['status'] != 'success':
                raise FailedAPICall("Error while deleting subjects: {}".format(json_data['message']))

        except:
            raise FailedAPICall("Failed to call delete_filtered_subjects")

        return json_data


class ImportData(VideoAIUser):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(ImportData, self).__init__(token=token, host=host, client_id=client_id,
                                         client_secret=client_secret,
                                         verbose=verbose)
        self.end_point = 'import_data'

    def request(self, input_file, data=None, request=None):

        if not os.path.isfile(input_file):
            raise FailedAPICall('Input file \'{}\' does not exists'.format(input_file))

        url = "{0}/{1}".format(self.base_url, self.end_point)

        try:
            if SIGN_REQUEST:
                self.sign_request(url, method="POST", data=data, request=request)

            if data is None:
                data = {}
            data['filename'] = input_file

            r = requests.post(url,
                              headers=self.header,
                              data=data,
                              allow_redirects=True,
                              verify=VERIFY_SSL)
            json_data = r.json()
        except:
            raise FailedAPICall('ImportData')

        if self.verbose:
            print print_http_response(r)

        if json_data['status'] != 'success':
            raise FailedAPICall("ImportData request failed: {}".format(r.json()['message']))

        return json_data

    def from_zipped_csv_files(self, input_file, data=None, wait_until_finished=True, request=None):

        json_data = self.request(input_file=input_file, data=data, request=request)

        if not wait_until_finished:
            return json_data

        json_data = self.wait(json_data)

        task = json_data['task']
        if not task['success']:
            print 'Failed ImportData: {0}'.format(task['message'])
            return task

        return json_data

    def accept_waiting_tasks(self, job_id, targets="", wait_until_finished=True, request=None):
        url = "{}/accept_waiting_tasks/{}".format(self.base_url, job_id)

        data = {'targets': targets}

        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)

            r = requests.post(url,
                              headers=self.header,
                              data=data,
                              allow_redirects=True,
                              verify=VERIFY_SSL)

            if self.verbose:
                print print_http_response(r)

            json_data = r.json()

            if not wait_until_finished:
                return json_data

            json_data = self.wait(json_data)

            task = json_data['task']
            if not task['success']:
                print 'Failed accepting subjects: {0}'.format(task['message'])
                return task
            return json_data

        except:
            raise FailedAPICall("Failed to call accept_waiting_tasks")


class ImportSubjects(VideoAIUser):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(ImportSubjects, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                             verbose=verbose)
        self.end_point = 'import_subjects'

    def request(self, input_file, request=None):

        if not os.path.isfile(input_file):
            raise FailedAPICall('Input file \'{}\' does not exists'.format(input_file))

        url = "{0}/{1}".format(self.base_url, self.end_point)

        try:
            if SIGN_REQUEST:
                self.sign_request(url, method="POST", request=request)

            files = {'input_file': open("{0}".format(input_file), mode='rb')}
            r = requests.post(url,
                              headers=self.header,
                              files=files,
                              allow_redirects=True,
                              verify=VERIFY_SSL)
            json_data = r.json()
        except:
            raise FailedAPICall('ImportSubjects')

        if self.verbose:
            print print_http_response(r)

        if json_data['status'] != 'success':
            raise FailedAPICall("ImportSubjects request failed: {}".format(r.json()['message']))

        return json_data

    def from_zip_file(self, input_file, wait_until_finished=True, request=None):

        json_data = self.request(input_file=input_file, request=request)

        if not wait_until_finished:
            return json_data

        json_data = self.wait(json_data)

        task = json_data['task']
        if not task['success']:
            print 'Failed ImportSubjects: {0}'.format(task['message'])
            return task

        return json_data

    def accept_waiting_tasks(self, job_id, targets="", request=None):

        url = "{}/accept_waiting_tasks/{}".format(self.base_url, job_id)

        data = {'targets': targets}
        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)

            r = requests.post(url,
                              headers=self.header,
                              data=data,
                              allow_redirects=True,
                              verify=VERIFY_SSL)

            json_data = r.json()

            if self.verbose:
                print print_http_response(r)

            if json_data['status'] != 'success':
                raise FailedAPICall("Error while accepting waiting tasks: {}".format(json_data['message']))

        except:
            raise FailedAPICall("Failed to call accept_waiting_tasks")

        return json_data

    def import_subjects_report(self, job_id, page=1, number_per_page=3, show_ignored=False, request=None):
        '''
        Get a list of all tasks or if job_id provided of all subtask of job_id
        :return:
        '''

        url = "{0}/import_subjects/{1}/{2}/{3}".format(self.base_url, job_id, page, number_per_page)
        url += "?show_ignored={}".format(show_ignored)

        if SIGN_REQUEST:
            self.sign_request(url, method="GET", request=request)

        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)

        if self.verbose:
            print_http_response(r)

        return r.json()


class ExportSubjects(VideoAIUser):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(ExportSubjects, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                             verbose=verbose)
        self.end_point = 'export_subjects'

    def request(self, request=None):

        print 'Requested export subjects'

        url = "{0}/{1}".format(self.base_url, self.end_point)

        try:
            if SIGN_REQUEST:
                self.sign_request(url, method="POST", request=request)

            r = requests.post(url,
                              headers=self.header,
                              allow_redirects=True,
                              verify=VERIFY_SSL)

            json_data = r.json()
        except:
            raise FailedAPICall('ExportSubjects')

        if self.verbose:
            print print_http_response(r)

        if json_data['status'] != 'success':
            raise FailedAPICall("ExportSubjects request failed: {}".format(r.json()['message']))

        return json_data

    def export(self, wait_until_finished=True, download=True, request=None):

        json_data = self.request(request=request)

        if not wait_until_finished:
            return json_data

        json_data = self.wait(json_data)

        task = json_data['task']

        if not task['success']:
            print 'Failed ExportSubjects: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['output_file'])

        return json_data

    def export_filtered_subjects(self, data, request=None):
        url = "{}/export_filtered_subjects".format(self.base_url)

        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)

            r = requests.post(url,
                              headers=self.header,
                              data=data,
                              allow_redirects=True,
                              verify=VERIFY_SSL)

            json_data = r.json()

            if self.verbose:
                print print_http_response(r)

            if json_data['status'] != 'success':
                raise FailedAPICall("Error while exporting subjects: {}".format(json_data['message']))

        except:
            raise FailedAPICall("Failed to call export_checked_subjects")

        return json_data

    def export_checked_subjects(self, job_id, targets="", request=None):

        url = "{}/export_checked_subjects/{}".format(self.base_url, job_id)

        data = {'targets': targets}

        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)

            r = requests.post(url,
                              headers=self.header,
                              data=data,
                              allow_redirects=True,
                              verify=VERIFY_SSL)

            json_data = r.json()

            if self.verbose:
                print print_http_response(r)

            if json_data['status'] != 'success':
                raise FailedAPICall("Error while exporting subjects: {}".format(json_data['message']))

        except:
            raise FailedAPICall("Failed to call export_checked_subjects")

        return json_data


# ExportLogs class
# Export all tasks and action
class ExportLogs(VideoAIUser):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(ExportLogs, self).__init__(token=token, host=host, client_id=client_id,
                                         client_secret=client_secret,
                                         verbose=verbose)
        self.end_point = 'export_logs'

    def request(self, format='csv', request=None):

        url = "{0}/{1}".format(self.base_url, self.end_point)
        data = {'format': format}
        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)

            r = requests.post(url,
                              headers=self.header,
                              data=data,
                              allow_redirects=True,
                              verify=VERIFY_SSL)

            json_data = r.json()
        except:
            raise FailedAPICall('ExportLogs')

        if self.verbose:
            print print_http_response(r)

        if json_data['status'] != 'success':
            raise FailedAPICall("ExportLogs request failed: {}".format(r.json()['message']))

        return json_data

    def export(self, wait_until_finished=True, download=True, format='cvs', request=None):

        json_data = self.request(format=format, request=request)

        if not wait_until_finished:
            return json_data

        json_data = self.wait(json_data)

        task = json_data['task']

        if not task['success']:
            print 'Failed ExportLogs: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['output_file'])

        return json_data

