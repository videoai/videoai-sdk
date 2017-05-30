import os
import base64
import requests
import oauth2 as oauth
import time
from os.path import expanduser
from configparser import ConfigParser
import json

VERIFY_SSL = False
SIGN_REQUEST = True

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
    print "Server: {}".format(r.headers['server'])
    if 'date' in r.headers:
        print "Date: {}".format(r.headers['date'])
    print json.dumps(r.json(), indent=4, sort_keys=True)

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
        lat = None
        lng = None
        try:
            ip_addr = request.remote_addr
            send_url = 'http://freegeoip.net/json/{}'.format(ip_addr)
            r = requests.get(send_url)
            j = json.loads(r.text)
            lat = j['latitude']
            lng = j['longitude']
            device_data = 'device_id="{}", latitude="{}", longitude="{}"'.format(ip_addr,
                                                                                 lat, lng)
        except:
            print("no ip or no location available")

    params = {
        'oauth_version': '1.0',
        'oauth_nonce': oauth_nonce,
        'oauth_timestamp': oauth_timestamp,
        'device_data': device_data
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

    header = req.to_header()
    header['Device'] = '{}'.format(device_data)
    header['Initial-User-Agent'] = initial_user_agent

    return header


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
            authentication_server = get_parameter(param=authentication_server, name='authentication_server', parser=parser)
        except:
            raise

        # Next we have
        data = {
            "email": email,
            "password": password
        }

        url = '{}/auth/api_login?client_id={}'.format(authentication_server, client_id)
        header = sign_request(url=url, client_id=client_id, client_secret=client_secret, data=data, method='POST', request=request)
        response = requests.post(url, data, headers=header, verify=VERIFY_SSL)
        json_response = json.loads(response.text)

        if 'status' in json_response and json_response['status'] == 'fail':
            raise AuthenticationError(json_response['message'])
        token = json_response['oauth_token']['token']
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

    def wait(self, response, request=None):

        task = response['task']

        # now we need to add client_id in the url
        # url = "{0}/{1}/{2}?client_id={3}".format(self.base_url, self.end_point, task['job_id'], self.client_id)
        url = "{0}/{1}/{2}".format(self.base_url, self.end_point, task['job_id'])

        if task['complete']:
            return task

        while not task['complete']:
            time.sleep(0.5)
            if SIGN_REQUEST:
                self.sign_request(url, data=None, method="GET", request=request)

            r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
            json_data = r.json()
            task = json_data['task']

            if self.verbose:
                print json.dumps(json_data, indent=4, sort_keys=True)

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

    def tasks(self, page=1, number_per_page=3, request=None):
        '''
        Get a list of all tasks
        :return:
        '''
        url = "{0}/{1}/{2}/{3}".format(self.base_url, self.end_point, page, number_per_page)

        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

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
        print("URL :{}".format(url))
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)
        
        if self.verbose:
            print_http_response(r)
       
        return r.json()

    def result_file(self, day_count, job_id, filename, request=None):
        '''
        Get a result file
        :return:
        '''
        url = "{}/results/{}/{}/{}".format(self.base_url, day_count, job_id, filename)
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="GET", request=request)

        r = requests.get(url, headers=self.header, allow_redirects=True, verify=VERIFY_SSL)

        if self.verbose:
            print print_http_response(r)

        if r.status_code == 200:
            return True, r.content, r.headers
        else:
            return False, None, None

class FaceLogImage(VideoAIUser):

    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(FaceLogImage, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                           verbose=verbose)
        self.end_point = 'face_log_image'

    def request(self, image_file, min_size=80, recognition=0, compare_threshold=0.6, top_n=1, location=None, request=None):

        file_size = os.path.getsize(image_file) / 1000000.0

        data = {
                'min_size': min_size,
                'recognition': recognition,
                'compare_threshold': compare_threshold,
                'top_n': top_n
               }
        if location is not None:
            data['location'] = location

        url = "{0}/{1}".format(self.base_url, self.end_point)

        files = {'image': open("{0}".format(image_file))}

        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)
            r = requests.post(url,
                              headers=self.header,
                              files=files,
                              data=data,
                              allow_redirects=True, verify=VERIFY_SSL)

            json_data = r.json()

            if self.verbose:
                print print_http_response(r)

            if json_data['status'] != 'success':
                raise FailedAPICall("Face Log request failed: {}". format(json_data['message']))

        except:
            raise FailedAPICall("Failed to call FaceLogImage")

        return json_data

    def apply(self, image_file, download=True, min_size=80, recognition=0, compare_threshold=0.6, top_n=1,
              wait_until_finished=True, local_output_dir='', location=None):

        json_data = self.request(image_file,
                                 min_size=min_size,
                                 recognition=recognition,
                                 compare_threshold=compare_threshold,
                                 top_n=top_n,
                                 location=location)

        if not wait_until_finished:
            return json_data

        json_data = self.wait(json_data)
        task = json_data['task']
        if not task['success']:
            print 'Failed FaceLogImage: {0}'.format(task['message'])
            return json_data

        if download:
            self.download_file(task['results_image'], local_dir=local_output_dir)
            for sighting in task['sightings']:
                self.download_file(sighting['thumbnail'], local_dir=local_output_dir)
        return json_data


class FaceLog(VideoAIUser):
    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(FaceLog, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                      verbose=verbose)
        self.end_point = 'face_log'

    def request(self, video_file, start_frame=0, max_frames=0, min_size=80,
                recognition=0, compare_threshold=0.6, top_n=1, subject_id='', location=None, request=None):

        file_size = os.path.getsize(video_file) / 1000000.0
        print 'Requested FaceLog on video {0} ({1} Mb)'.format(video_file, file_size)
        data = {
            'start_frame': start_frame,
            'max_frames': max_frames,
            'min_size': min_size,
            'recognition': recognition,
            'compare_threshold': compare_threshold,
            'top_n': top_n,
            'subject_id': subject_id
        }
        if location is not None:
            data['location'] = location

        print("location : {}".format(data['location']))

        url = "{0}/{1}".format(self.base_url, self.end_point)

        files = {'video': open("{0}".format(video_file))}
        try:

            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST", request=request)

            r = requests.post(url, headers=self.header, files=files, data=data, allow_redirects=True, verify=VERIFY_SSL)
            json_data = r.json()

            if self.verbose:
                print print_http_response(r)

            if json_data['status'] != 'success':
                raise FailedAPICall("face_log request failed: {}". format(r.json()['message']))

        except:
            raise FailedAPICall("Failed to run FaceLog")
        return json_data

    def apply(self, video_file, download=True, start_frame=0, max_frames=0, min_size=80, recognition=0,
              compare_threshold=0.6, top_n=1, subject_id='', wait_until_finished=True, local_output_dir='', location=None):

        json_data = self.request(video_file,
                                 recognition=recognition,
                                 compare_threshold=compare_threshold,
                                 top_n=top_n,
                                 start_frame=start_frame,
                                 max_frames=max_frames,
                                 min_size=min_size,
                                 subject_id=subject_id,
                                 location=location)

        if not wait_until_finished:
            return json_data

        json_data = self.wait(json_data)
        task = json_data['task']
        if not task['success']:
            print 'Failed FaceLog: {0}'.format(task['message'])
            return json_data

        if download:
            self.download_file(task['results_video'], local_dir=local_output_dir)
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
            'gallery': open('{}'.format(gallery))
        }

        if probe1:
            files['probe1'] = open('{}'.format(probe1))

        if probe2:
            files['probe2'] = open('{}'.format(probe2))

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
            raise FailedAPICall("Face Authenticate request failed: {}". format(r.json()['message']))

        return json_data


    def apply(self, gallery, probe1='', probe2='', download=True, compare_threshold=0.6, wait_until_finished=True):

        json_data = self.request(gallery=gallery, probe1=probe1, probe2=probe2, compare_threshold=compare_threshold)

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
            data = {'face_log_id': face_log_id}

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
            raise FailedAPICall("BuildVideo request failed: {}". format(r.json()['message']))

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

    def from_face_log(self, face_log_id, download=True, wait_until_finished=True):

        json_data = self.request(face_log_id=face_log_id)

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
            data = {'face_log_image_id': face_log_image_id}

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
            raise FailedAPICall("BuildImage request failed: {}". format(r.json()['message']))

        return json_data

    def from_sighting(self, sighting_id, download=True, wait_until_finished=True):

        json_data = self.request(sighting_id=sighting_id)

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

    def from_face_log_image(self, face_log_image_id, download=True, wait_until_finished=True):

        json_data = self.request(face_log_image_id=face_log_image_id)

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


class ImportSubjects(VideoAIUser):

    def __init__(self, token, host, client_id, client_secret, verbose=False):
        super(ImportSubjects, self).__init__(token=token, host=host, client_id=client_id, client_secret=client_secret,
                                               verbose=verbose)
        self.end_point = 'import_subjects'

    def request(self, input_file, request=None):

        print 'Requested import subjects'

        if not os.path.isfile(input_file) :
            raise FailedAPICall('Input file \'{}\' does not exists'.format(input_file))

        url = "{0}/{1}".format(self.base_url, self.end_point)
        
        try:
            if SIGN_REQUEST:
                self.sign_request(url, method="POST", request=request)
       

            files = {'input_file': open("{0}".format(input_file))}
            r = requests.post(url,
                              headers=self.header,
                              files=files,
                              allow_redirects=True,
                              verify=VERIFY_SSL)
            print_http_response(r)
            json_data = r.json()
        except:
            raise FailedAPICall('ImportSubjects')
        
    
        if self.verbose:
            print print_http_response(r)

        if json_data['status'] != 'success':
            raise FailedAPICall("ImportSubjects request failed: {}". format(r.json()['message']))

        return json_data

    def from_zip_file(self, input_file, wait_until_finished=True):

        json_data = self.request(input_file=input_file)

        if not wait_until_finished:
            return json_data

        json_data = self.wait(json_data)

        task = json_data['task']
        if not task['success']:
            print 'Failed ImportSubjects: {0}'.format(task['message'])
            return task

        return json_data 


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
            print_http_response(r)
            json_data = r.json()
        except:
            raise FailedAPICall('ExportSubjects')
        
    
        if self.verbose:
            print print_http_response(r)

        if json_data['status'] != 'success':
            raise FailedAPICall("ExportSubjects request failed: {}". format(r.json()['message']))

        return json_data

    def export(self, wait_until_finished=True, download=True):

        json_data = self.request()

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

