import os
import base64
import requests
import time
from os.path import expanduser
from configparser import ConfigParser

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

    def __init__(self,  host='', key_file='', api_id='', api_secret='', verbose=False):

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

        # We need some keys
        if not api_id or not api_secret:
            if not parser.has_option(section, 'apiKey_id') or not parser.has_option(section, 'apiKey_secret'):
                raise Exception('No valid configuration found for VideoAPI keys')
            api_id = parser.get('videoai.net', 'apiKey_id')
            api_secret = parser.get('videoai.net', 'apiKey_secret')

        # Lets make the auth header
        api_key = "{0}:{1}".format(api_id, api_secret)
        basic_auth_header = "Basic {0}".format(base64.b64encode(api_key))
        self.header = {'Authorization': basic_auth_header}
        self.verbose = verbose
        self.end_point = 'task'
        print "Using VideoAI host '{}'".format(self.base_url)

    def wait(self, task):

        url = "{0}/{1}/{2}".format(self.base_url, self.end_point, task['job_id'])

        if task['complete']:
            return task

        while not task['complete']:
            time.sleep(0.5)
            r = requests.get(url, headers=self.header, allow_redirects=True)

            if r.json()['status'] != 'success':
                raise Exception("Polling failed: {}". format(r.json()['message']))
            task = r.json()['task']
            if self.verbose:
                print task

        if self.verbose:
            print print_http_response(r)

        return task

    def download_file(self, url, local_filename='', local_dir=''):
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
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return local_filename


    def download_with_authentication(self, end_point, local_filename=''):
        if not local_filename:
            local_filename = end_point.split('/')[-1]
        url = '{}{}'.format(self.base_url, end_point)
        print 'Downloading {0} to {1}'.format(url, local_filename)
        r = requests.get(url,  headers=self.header, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return local_filename


    def tasks(self, page=1, number_per_page=3):
        '''
        Get a list of all tasks
        :return:
        '''
        url = "{0}/{1}/{2}/{3}".format(self.base_url, self.end_point, page, number_per_page)
        print url
        r = requests.get(url, headers=self.header, allow_redirects=True)
        if self.verbose:
            print_http_response(r)
        return r.json()

    def task(self, job_id):
        '''
        Get a specific task
        :return:
        '''
        url = "{0}/{1}/{2}".format(self.base_url, self.end_point, job_id)
        r = requests.get(url, headers=self.header, allow_redirects=True)
        
	if self.verbose:
            print_http_response(r)
        return r.json()


class KamCheck(VideoAIUser):

    def __init__(self, host='', key_file = '', api_id='', api_secret='', verbose=False):
        super(KamCheck, self).__init__(host=host, key_file=key_file, api_id=api_id, api_secret=api_secret, verbose=verbose)
        self.end_point = 'kamcheck'

    def request(self, image_file, video_file):

        image_file_size = os.path.getsize(image_file)/1000000.0
        video_file_size = os.path.getsize(video_file)/1000000.0
        self.end_point = 'kamcheck'
        print 'Requested KamCheck on image {0} ({1} Mb) and video {2} ({3} Mb)'.format(image_file, image_file_size, video_file, video_file_size)
        url = "{0}/{1}".format(self.base_url, self.end_point)
        files = {'image': open("{0}".format(image_file)),
                 'video': open("{0}".format(video_file))
        }
        r = requests.post(url, headers=self.header, files=files,  allow_redirects=True)

        if r.json()['status'] != 'success':
            print print_http_response(r)
            raise Exception("KamCheck request failed: {}". format(r.json()['message']))

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
            print 'Reference {0}, video {1}, probability of tampering {2}%'.format(image_file, video_file, task['probability'])
        return task
    
    def request_get_reference_image(self, video_file):

        video_file_size = os.path.getsize(video_file)/1000000.0
        self.end_point = 'kamcheck_get_reference'
        print 'Requested KamCheckGetReference on video {0} ({1} Mb)'.format(video_file, video_file_size)
        url = "{0}/{1}".format(self.base_url, self.end_point)
        files = {
                 'video': open("{0}".format(video_file))
        }
        r = requests.post(url, headers=self.header, files=files,  allow_redirects=True)

        if r.json()['status'] != 'success':
            print print_http_response(r)
            raise Exception("KamCheck GetReference Image request failed: {}". format(r.json()['message']))

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
            print 'Video {0}, Frame {1} Reference Image {2}'.format(video_file, task['frame_number'], task['reference_image'])
        if download:
            self.download_file(task['reference_image'])
        return task


class AlarmVerification(VideoAIUser):

    def __init__(self, host='', key_file='', api_id='', api_secret='', verbose=False):
        super(AlarmVerification, self).__init__(host=host, key_file=key_file, api_id=api_id, api_secret=api_secret, verbose=verbose)
        self.end_point = 'alarm_verification'

    def request(self, video_file):
        file_size = os.path.getsize(video_file)/1000000.0
        print 'Requested AlarmVerification on file {0} ({1} Mb)'.format(video_file, file_size)

        url = "{0}/{1}".format(self.base_url, self.end_point)
        files = {'video': open("{0}".format(video_file))}
        r = requests.post(url, headers=self.header, files=files,  allow_redirects=True)

        if self.verbose:
            print print_http_response(r)

        if r.json()['status'] != 'success':
            print print_http_response(r)
            raise Exception("Alarm Verification request failed: {}". format(r.json()['message']))

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

    def __init__(self, algorithm='stabilisation', host='', key_file='', api_id='', api_secret='', verbose=False):
        super(Enhance, self).__init__(host=host, key_file=key_file, api_id=api_id, api_secret=api_secret, verbose=verbose)
        self.algorithm = algorithm
        self.end_point = 'enhance'

    def request(self, video_file, max_frames):
        file_size = os.path.getsize(video_file)/1000000.0
        print 'Requested stabilisation on file {0} ({1} Mb)'.format(video_file, file_size)

        url = "{0}/{1}".format(self.base_url, self.end_point)
        files = {'video': open("{0}".format(video_file))}
        data = {'algorithm': self.algorithm, 'max_frames':max_frames }
        r = requests.post(url, headers=self.header, data=data, files=files,  allow_redirects=True)

        if self.verbose:
            print print_http_response(r)

        if r.json()['status'] != 'success':
            print print_http_response(r)
            raise Exception("Stabilisation request failed: {}". format(r.json()['message']))

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
        super(FaceDetectImage, self).__init__(host=host, key_file=key_file, api_id=api_id, api_secret=api_secret, verbose=verbose)
        self.end_point = 'face_detect_image'

    def request(self, image_file, blur, min_size):

        file_size = os.path.getsize(image_file)/1000000.0
        print 'Requested FaceDetectImage on {0} ({1} Mb)'.format(image_file, file_size)
        data = {'blur': blur, 'min_size': min_size}

        url = "{0}/{1}".format(self.base_url, self.end_point)

        files = {'image': open("{0}".format(image_file))}
        try:
            r = requests.post(url, headers=self.header, files=files,  data=data, allow_redirects=True)
        except:
            return

        if r.json()['status'] != 'success':
            print print_http_response(r)
            raise Exception("Face Detect request failed: {}". format(r.json()['message']))

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
            self.download_file(task['results_xml'])
        return task


class FaceDetect(VideoAIUser):

    def __init__(self, host='', key_file='', api_id='', api_secret='', verbose=False):
        super(FaceDetect, self).__init__(host=host, key_file=key_file, api_id=api_id, api_secret=api_secret, verbose=verbose)
        self.end_point = 'face_detect'

    def request(self, video_file, blur=0, start_frame=0, max_frames=0, min_size=30):

        file_size = os.path.getsize(video_file)/1000000.0
        print 'Requested FaceDetect on video {0} ({1} Mb)'.format(video_file, file_size)
        data = {'blur': blur, 'start_frame': start_frame, 'max_frames': max_frames, 'min_size': min_size}

        url = "{0}/{1}".format(self.base_url, self.end_point)
        files = {'video': open("{0}".format(video_file))}

        r = requests.post(url, headers=self.header, files=files,  data=data, allow_redirects=True)

        if r.json()['status'] != 'success':
            print print_http_response(r)
            raise Exception("Face Detect request failed: {}". format(r.json()['message']))

        # while the task is not complete, lets keep checking it
        task = r.json()['task']

        if self.verbose:
            print print_http_response(r)

        return task

    def apply(self, video_file, download=True, blur=0, start_frame=0, max_frames=0, min_size=30, wait_until_finished=True):

        task = self.request(video_file, blur, start_frame, max_frames, min_size)

        if not wait_until_finished:
            return task

        task = self.wait(task)

        if not task['success']:
            print 'Failed FaceDetect: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['results_video'])
            self.download_file(task['results_xml'])

        return task


class FaceLogImage(VideoAIUser):

    def __init__(self, host='', key_file='', api_id='', api_secret='', verbose=False):
        super(FaceLogImage, self).__init__(host=host, key_file=key_file, api_id=api_id, api_secret=api_secret, verbose=verbose)
        self.end_point = 'face_log_image'

    def request(self, image_file, min_size=80, recognition=0, compare_threshold=0.75):

        file_size = os.path.getsize(image_file)/1000000.0
        print 'Requested FaceLogImage on {0} ({1} Mb)'.format(image_file, file_size)

        data = {'min_size': min_size, 'recognition': recognition, 'compare_threshold': compare_threshold}

        url = "{0}/{1}".format(self.base_url, self.end_point)

        files = {'image': open("{0}".format(image_file))}

        try:
            r = requests.post(url, headers=self.header, files=files,  data=data, allow_redirects=True)
        except:
            return

        if r.json()['status'] != 'success':
            print print_http_response(r)
            raise Exception("Face Log request failed: {}". format(r.json()['message']))

        # while the task is not complete, lets keep checking it
        task = r.json()['task']
        if self.verbose:
            print print_http_response(r)

        return task

    def apply(self, image_file, download=True, min_size=80, recognition=0, compare_threshold=0.75,
              wait_until_finished=True, local_output_dir=''):

        task = self.request(image_file, min_size=min_size, recognition=recognition, compare_threshold=compare_threshold)

        if not wait_until_finished:
            return task

        task = self.wait(task)

        if not task['success']:
            print 'Failed FaceLogImage: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['results_image'], local_dir=local_output_dir)
            self.download_file(task['results_xml'], local_dir=local_output_dir)
        return task


class FaceLog(VideoAIUser):

    def __init__(self, host='', key_file='', api_id='', api_secret='', verbose=False):
        super(FaceLog, self).__init__(host=host, key_file=key_file, api_id=api_id, api_secret=api_secret, verbose=verbose)
        self.end_point = 'face_log'

    def request(self, video_file, start_frame=0, max_frames=0, min_size=80, recognition=0, compare_threshold=0.75):

        file_size = os.path.getsize(video_file)/1000000.0
        print 'Requested FaceLog on video {0} ({1} Mb)'.format(video_file, file_size)
        data = { 
                'start_frame': start_frame, 
                'max_frames': max_frames, 
                'recognition': recognition,
                'compare_threshold': compare_threshold,
                'min_size': min_size, 
                }

        url = "{0}/{1}".format(self.base_url, self.end_point)

        files = {'video': open("{0}".format(video_file))}

        r = requests.post(url, headers=self.header, files=files,  data=data, allow_redirects=True)

        if r.json()['status'] != 'success':
            print print_http_response(r)
            raise Exception("face_log request failed: {}". format(r.json()['message']))

        # while the task is not complete, lets keep checking it
        task = r.json()['task']
        if self.verbose:
            print print_http_response(r)

        return task

    def apply(self, video_file, download=True, start_frame=0, max_frames=0, min_size=80, recognition=0,
              compare_threshold=0.75, wait_until_finished=True, local_output_dir=''):
        task = self.request(video_file, recognition=recognition, compare_threshold=compare_threshold, start_frame=start_frame, max_frames=max_frames, min_size=min_size)

        if not wait_until_finished:
            return task

        task = self.wait(task)

        if not task['success']:
            print 'Failed FaceLog: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['results_video'], local_dir=local_output_dir)
            self.download_file(task['results_xml'], local_dir=local_output_dir)

            for sighting in task['sightings']:
                self.download_file(sighting['thumbnail'], local_dir=local_output_dir)
        return task


class SafeZone2d(VideoAIUser):

    def __init__(self, host='', key_file='', api_id='', api_secret='', verbose=False):
        super(SafeZone2d, self).__init__(host=host, key_file=key_file, api_id=api_id, api_secret=api_secret, verbose=verbose)
        self.end_point = 'safezone_2d'

    def request(self, video_file, start_frame=0, max_frames=0):

        file_size = os.path.getsize(video_file)/1000000.0
        print 'Requested SafeZone2d on video {0} ({1} Mb)'.format(video_file, file_size)
        data = {'start_frame': start_frame, 'max_frames': max_frames}

        url = "{0}/{1}".format(self.base_url, self.end_point)
        files = {'video': open("{0}".format(video_file))}

        r = requests.post(url, headers=self.header, files=files,  data=data, allow_redirects=True)

        if r.json()['status'] != 'success':
            print print_http_response(r)
            raise Exception("safezone_2d request failed: {}". format(r.json()['message']))

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
            self.download_file(task['results_xml'])

        return task


