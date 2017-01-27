import os
import base64
import requests
import oauth2 as oauth
import time
from os.path import expanduser
from configparser import ConfigParser

SIGN_REQUEST = True


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


class VideoAIUser(object):
    def __init__(self, token, host='', key_file='', verbose=False):
        # Always try and read a configuration file.  Although it is not an error if we can not find one
        if not key_file:
            home = expanduser("~")
            key_file = os.path.join(home, '.videoai')
        parser = ConfigParser()
        parser.read(key_file)
        section = 'videoai.net'

        # Have we got a host, if not we try and get one?
        if not host:
            if parser.has_option(section, 'host'):
                host = parser.get(section, 'host')
            else:
                host = 'https://api.videoai.net'
        self.base_url = host

        # if the request is not signed token is provided in Authorization header Basic
        if not SIGN_REQUEST:
            formatted_token = "{0}:no_use".format(token)
            basic_auth_header = "Basic {0}".format(formatted_token)
            self.header = {'Authorization': basic_auth_header}

        # Lets make the auth header
        # keep some information
        if parser.has_option(section, 'client_id'):
            self.client_id = parser.get(section, 'client_id')
        if parser.has_option(section, 'client_secret'):
            self.client_secret = parser.get(section, 'client_secret')
        self.token = token

        self.verbose = verbose
        self.end_point = 'task'
        print ("client_id / client_secret {}/{}".format(self.client_id, self.client_secret))
        print "Using VideoAI host '{}'".format(self.base_url)

    # This function will sign a request using, method, url (with parameters), data (form parameters)
    #       if oauth_nonce and oauth_timestamp are not None it will use those provided ==> used to check signature
    #       if oauth_nonce and oauth_timestamp are None they will be generated
    # and return the header containing signature
    def sign_request(self, url, data=None, method="GET", oauth_nonce=None, oauth_timestamp=None):

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
        token = oauth.Token(key=self.token, secret="")
        consumer = oauth.Consumer(key=self.client_id, secret=self.client_secret)

        # Set our token/key parameters
        params['oauth_token'] = token.key
        params['oauth_consumer_key'] = consumer.key

        # Create our request. Change method, etc. accordingly.
        print("----- Parameters: {}".format(params))
        print("----- URL {}".format(url))
        print("----- method {}".format(method))

        req = oauth.Request(method=method.upper(), url=url, parameters=params)

        # Sign the request.
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, consumer, token)

        self.header = req.to_header()

    def wait(self, task):
        # now we need to add client_id in the url
        url = "{0}/{1}/{2}?client_id={3}".format(self.base_url, self.end_point, task['job_id'], self.client_id)

        if task['complete']:
            return task

        while not task['complete']:
            time.sleep(0.5)
            if SIGN_REQUEST:
                self.sign_request(url, data=None, method="GET")

            r = requests.get(url, headers=self.header, allow_redirects=True)

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


class KamCheck(VideoAIUser):
    def __init__(self, token, host='', key_file='', verbose=False):
        super(KamCheck, self).__init__(token=token, host=host, key_file=key_file, verbose=verbose)
        self.end_point = 'kamcheck'

    def request(self, image_file, video_file):

        image_file_size = os.path.getsize(image_file) / 1000000.0
        video_file_size = os.path.getsize(video_file) / 1000000.0
        self.end_point = 'kamcheck'
        print 'Requested KamCheck on image {0} ({1} Mb) and video {2} ({3} Mb)'.format(image_file, image_file_size,
                                                                                       video_file, video_file_size)
        url = "{0}/{1}?client_id={2}".format(self.base_url, self.end_point, self.client_id)
        files = {'image': open("{0}".format(image_file)),
                 'video': open("{0}".format(video_file))
                 }
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="POST")

        r = requests.post(url, headers=self.header, files=files, allow_redirects=True)

        if r.json()['status'] != 'success':
            print print_http_response(r)
            # raise Exception("KamCheck request failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

        if self.verbose:
            print print_http_response(r)

        return r.json()['task']

    def apply(self, image_file, video_file, wait_until_finished=True):
        task = self.request(image_file, video_file)

        if not wait_until_finished:
            return task

        task = self.wait(task)
        if not task['success']:
            print 'Failed Kamcheck: {0}'.format(task['message'])
        else:
            print 'Reference {0}, video {1}, probability of tampering {2}%'.format(image_file, video_file,
                                                                                   task['probability'])
        return task

    def request_get_reference_image(self, video_file):

        video_file_size = os.path.getsize(video_file) / 1000000.0
        self.end_point = 'kamcheck_get_reference'
        print 'Requested KamCheckGetReference on video {0} ({1} Mb)'.format(video_file, video_file_size)
        url = "{0}/{1}?client_id={2}".format(self.base_url, self.end_point, self.client_id)
        files = {
            'video': open("{0}".format(video_file))
        }
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="POST")
        r = requests.post(url, headers=self.header, files=files, allow_redirects=True)

        if r.json()['status'] != 'success':
            print print_http_response(r)
            # raise Exception("KamCheck GetReference Image request failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

        if self.verbose:
            print print_http_response(r)

        return r.json()['task']

    def get_reference_image(self, video_file, download=True, wait_until_finished=True):
        task = self.request_get_reference_image(video_file)

        if not wait_until_finished:
            return task

        task = self.wait(task)
        if not task['success']:
            print 'Failed Kamcheck: {0}'.format(task['message'])
        else:
            print 'Video {0}, Frame {1} Reference Image {2}'.format(video_file, task['frame_number'],
                                                                    task['reference_image'])
        if download:
            self.download_file(task['reference_image'])
        return task


class AlarmVerification(VideoAIUser):
    def __init__(self, token, host='', key_file='', verbose=False):
        super(AlarmVerification, self).__init__(token=token, host=host, key_file=key_file, verbose=verbose)
        self.end_point = 'alarm_verification'

    def request(self, video_file):
        file_size = os.path.getsize(video_file) / 1000000.0
        print 'Requested AlarmVerification on file {0} ({1} Mb)'.format(video_file, file_size)

        url = "{0}/{1}?client_id={2}".format(self.base_url, self.end_point, self.client_id)
        files = {'video': open("{0}".format(video_file))}
        if SIGN_REQUEST:
            self.sign_request(url, data=None, method="POST")
        r = requests.post(url, headers=self.header, files=files, allow_redirects=True)

        if self.verbose:
            print print_http_response(r)

        if r.json()['status'] != 'success':
            print print_http_response(r)
            # raise Exception("Alarm Verification request failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

        return r.json()['task']

    def apply(self, video_file, download=True, wait_until_finished=True):

        # do initial request
        task = self.request(video_file)

        if not wait_until_finished:
            return task

        # keep checking until it is done
        task = self.wait(task)

        # has the task been successful?
        if not task['success']:
            print 'Failed AlarmVerification: {0}'.format(task['message'])
            return task

        print 'AlarmVerification probability of alarm {}%'.format(task['probability'])
        if download:
            self.download_file(task['results_video'])
        return task


class Enhance(VideoAIUser):
    def __init__(self, token, algorithm='stabilisation', host='', key_file='', verbose=False):
        super(Enhance, self).__init__(token=token, host=host, key_file=key_file, verbose=verbose)

    def __init__(self, algorithm='stabilisation', host='', key_file='', api_id='', api_secret='', verbose=False):
        super(Enhance, self).__init__(host=host, key_file=key_file, api_id=api_id, api_secret=api_secret,
                                      verbose=verbose)
        self.algorithm = algorithm
        self.end_point = 'enhance'

    def request(self, video_file, max_frames):
        file_size = os.path.getsize(video_file) / 1000000.0
        print 'Requested stabilisation on file {0} ({1} Mb)'.format(video_file, file_size)

        url = "{0}/{1}?client_id={2}".format(self.base_url, self.end_point, self.client_id)
        files = {'video': open("{0}".format(video_file))}
        data = {'algorithm': self.algorithm, 'max_frames': max_frames}
        if SIGN_REQUEST:
            self.sign_request(url, data=data, method="POST")
        r = requests.post(url, headers=self.header, data=data, files=files, allow_redirects=True)

        if self.verbose:
            print print_http_response(r)

        if r.json()['status'] != 'success':
            print print_http_response(r)
            # raise Exception("Stabilisation request failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

        return r.json()['task']

    def apply(self, video_file, download=True, wait_until_finished=True, max_frames=0):

        # do initial request
        task = self.request(video_file, max_frames)

        if not wait_until_finished:
            return task

        # keep checking until it is done
        task = self.wait(task)

        # has the task been successful?
        if not task['success']:
            print 'Failed Enhance: {0}'.format(task['message'])
            return task

        print task['message']
        if download:
            self.download_file(task['results_video'])
        return task


class FaceDetectImage(VideoAIUser):
    def __init__(self, host='', key_file='', api_id='', api_secret='', verbose=False):
        super(FaceDetectImage, self).__init__(host=host, key_file=key_file, api_id=api_id, api_secret=api_secret,
                                              verbose=verbose)
        self.end_point = 'face_detect_image'

    def request(self, image_file, blur, min_size):

        file_size = os.path.getsize(image_file) / 1000000.0
        print 'Requested FaceDetectImage on {0} ({1} Mb)'.format(image_file, file_size)
        data = {'blur': blur, 'min_size': min_size}

        url = "{0}/{1}?client_id={2}".format(self.base_url, self.end_point, self.client_id)

        files = {'image': open("{0}".format(image_file))}
        try:
            if SIGN_REQUEST:
                self.sign_request(url, data=data, method="POST")
            r = requests.post(url, headers=self.header, files=files, data=data, allow_redirects=True)
        except:
            return

        if r.json()['status'] != 'success':
            print print_http_response(r)
            # raise Exception("Face Detect request failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

        # while the task is not complete, lets keep checking it
        task = r.json()['task']
        if self.verbose:
            print print_http_response(r)

        return task

    def apply(self, image_file, download=True, blur=0, min_size=30, wait_until_finished=True):

        task = self.request(image_file, blur, min_size)

        if not wait_until_finished:
            return task

        task = self.wait(task)

        if not task['success']:
            print 'Failed FaceDetectImage: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['results_image'])
        return task


class FaceDetect(VideoAIUser):
    def __init__(self, host='', key_file='', api_id='', api_secret='', verbose=False):
        super(FaceDetect, self).__init__(host=host, key_file=key_file, api_id=api_id, api_secret=api_secret,
                                         verbose=verbose)
        self.end_point = 'face_detect'

    def request(self, video_file, blur=0, start_frame=0, max_frames=0, min_size=30):

        file_size = os.path.getsize(video_file) / 1000000.0
        print 'Requested FaceDetect on video {0} ({1} Mb)'.format(video_file, file_size)
        data = {'blur': blur, 'start_frame': start_frame, 'max_frames': max_frames, 'min_size': min_size}

        url = "{0}/{1}?client_id={2}".format(self.base_url, self.end_point, self.client_id)
        files = {'video': open("{0}".format(video_file))}

        if SIGN_REQUEST:
            self.sign_request(url, data=data, method="POST")
        r = requests.post(url, headers=self.header, files=files, data=data, allow_redirects=True)

        if r.json()['status'] != 'success':
            print print_http_response(r)
            # raise Exception("Face Detect request failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

        # while the task is not complete, lets keep checking it
        task = r.json()['task']

        if self.verbose:
            print print_http_response(r)

        return task

    def apply(self, video_file, download=True, blur=0, start_frame=0, max_frames=0, min_size=30,
              wait_until_finished=True):

        task = self.request(video_file, blur, start_frame, max_frames, min_size)

        if not wait_until_finished:
            return task

        task = self.wait(task)

        if not task['success']:
            print 'Failed FaceDetect: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['results_video'])

        return task


class FaceLogImage(VideoAIUser):
    def __init__(self, token, host='', key_file='', verbose=False):
        super(FaceLogImage, self).__init__(token=token, host=host, key_file=key_file, verbose=verbose)
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

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

        # while the task is not complete, lets keep checking it
        task = r.json()['task']
        if self.verbose:
            print print_http_response(r)

        return task

    def apply(self, image_file, download=True, min_size=80, recognition=0, compare_threshold=0.5,
              wait_until_finished=True, local_output_dir=''):

        json_response = self.request(image_file, min_size=min_size, recognition=recognition,
                                     compare_threshold=compare_threshold)

        if json_response['status'] != "success":
            return json_response

        task = json_response['task']

        print("Task: {}".format(task))
        if not wait_until_finished:
            return json_response
            # return task

        print("before wait")
        task = self.wait(task)
        print("after wait")
        if not task['success']:
            print 'Failed FaceLogImage: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['results_image'], local_dir=local_output_dir)
            for sighting in task['sightings']:
                self.download_file(sighting['thumbnail'], local_dir=local_output_dir)
        return task


class FaceLog(VideoAIUser):
    def __init__(self, token, host='', key_file='', verbose=False):
        super(FaceLog, self).__init__(token=token, host=host, key_file=key_file, verbose=verbose)
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
        print url

        r = requests.post(url, headers=self.header, files=files, data=data, allow_redirects=True)
        if r.json()['status'] != 'success':
            print print_http_response(r)
            # raise Exception("face_log request failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

        # while the task is not complete, lets keep checking it
        task = r.json()['task']
        if self.verbose:
            print print_http_response(r)

        return task

    def apply(self, video_file, download=True, start_frame=0, max_frames=0, min_size=80, recognition=0,
              compare_threshold=0.6, wait_until_finished=True, local_output_dir=''):

        task = self.request(video_file, recognition=recognition, compare_threshold=compare_threshold,
                            start_frame=start_frame, max_frames=max_frames, min_size=min_size)

        if not wait_until_finished:
            return task

        task = self.wait(task)

        if not task['success']:
            print 'Failed FaceLog: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['results_video'], local_dir=local_output_dir)

            for sighting in task['sightings']:
                self.download_file(sighting['thumbnail'], local_dir=local_output_dir)
        return task


class FaceAuthenticate(VideoAIUser):
    def __init__(self, token, host='', key_file='', verbose=False):
        super(FaceAuthenticate, self).__init__(token=token, host=host, key_file=key_file, verbose=verbose)
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

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

        # while the task is not complete, lets keep checking it
        task = r.json()['task']
        if self.verbose:
            print print_http_response(r)

        return task

    def apply(self, gallery, probe1='', probe2='', download=True, compare_threshold=0.6, wait_until_finished=True):

        task = self.request(gallery=gallery, probe1=probe1, probe2=probe2, compare_threshold=compare_threshold)

        if not wait_until_finished:
            return task

        task = self.wait(task)

        if not task['success']:
            print 'Failed FaceLogImage: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['gallery_thumbnail'])
            self.download_file(task['probe1_thumbnail'])
            if task['probe2_thumbnail']:
                self.download_file(task['probe2_thumbnail'])
        return task


class SafeZone2d(VideoAIUser):
    def __init__(self, token, host='', key_file='', verbose=False):
        super(SafeZone2d, self).__init__(token=token, host=host, key_file=key_file, verbose=verbose)
        self.end_point = 'safezone_2d'

    def request(self, video_file, start_frame=0, max_frames=0):

        file_size = os.path.getsize(video_file) / 1000000.0
        print 'Requested SafeZone2d on video {0} ({1} Mb)'.format(video_file, file_size)
        data = {'start_frame': start_frame, 'max_frames': max_frames}

        url = "{0}/{1}?client_id={2}".format(self.base_url, self.end_point, self.client_id)
        files = {'video': open("{0}".format(video_file))}

        if SIGN_REQUEST:
            self.sign_request(url, data=data, method="POST")

        r = requests.post(url, headers=self.header, files=files, data=data, allow_redirects=True)

        if r.json()['status'] != 'success':
            print print_http_response(r)
            # raise Exception("safezone_2d request failed: {}". format(r.json()['message']))

        # We should return the complete json containing a status to be able to react to error
        # @@ TODO lets try it
        return r.json()

        # while the task is not complete, lets keep checking it
        task = r.json()['task']
        if self.verbose:
            print print_http_response(r)

        return task

    def apply(self, video_file, download=True, start_frame=0, max_frames=0, wait_until_finished=True):

        task = self.request(video_file, start_frame, max_frames)

        if not wait_until_finished:
            return task

        task = self.wait(task)

        if not task['success']:
            print 'Failed SafeZone2d: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['results_video'])

        return task


