import os
import configparser
import base64
import requests
import time
from os.path import expanduser

class VideoAIUser(object):

    def __init__(self, key_file, verbose):
        if not key_file:
            home = expanduser("~")
            key_file = os.path.join(home, '.videoai')
        config = configparser.ConfigParser()
        config.read(key_file)
        keys = config['videoai.net']
        apiKey = "{0}:{1}".format(keys['apiKey_id'], keys['apiKey_secret'])
        basic_auth_header = "Basic {0}".format(base64.b64encode(apiKey))
        self.header = {'Authorization': basic_auth_header}
        self.base_url = "https://api.videoai.net"
        self.verbose = verbose
        # base_url = "http://localhost:5000"

    def download_file(self, url, local_filename=''):
        if not local_filename:
            local_filename = url.split('/')[-1]
        print 'Downloading {0} to {1}'.format(url, local_filename)
        r = requests.get(url, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return local_filename


class KamCheck(VideoAIUser):

    def __init__(self, key_file = '', verbose=False):
        super(KamCheck, self).__init__(key_file=key_file, verbose=verbose)
        self.end_point = 'kamcheck'

    def apply(self, image_file, video_file):
        image_file_size = os.path.getsize(image_file)/1000000.0
        video_file_size = os.path.getsize(video_file)/1000000.0
        print 'Requested KamCheck on image {0} ({1} Mb) and video {2} ({3} Mb)'.format(image_file, image_file_size, video_file, video_file_size)
        url = "{0}/{1}".format(self.base_url, self.end_point)
        files = {'image': open("{0}".format(image_file)),
                 'video': open("{0}".format(video_file))
        }

        r = requests.post(url, headers=self.header, files=files,  allow_redirects=True)

        # while the task is not complete, lets keep checking it
        task = r.json()['task']
        while not task['complete']:
            time.sleep(0.5)
            job_id = task['job_id']
            url = "{0}/{1}/{2}".format(self.base_url, self.end_point, job_id)
            response = requests.get(url, headers=self.header, allow_redirects=True)
            task = response.json()['task']
            if self.verbose:
                print task
        print 'Reference {0}, video {1}, probability of tampering {2}%'.format(image_file, video_file, task['probability'])
        return task


class AlarmVerification(VideoAIUser):

    def __init__(self, key_file = '', verbose=False):
        super(AlarmVerification, self).__init__(key_file=key_file, verbose=verbose)
        self.end_point = 'alarm_verification'

    def apply(self, video_file, download=True):

        file_size = os.path.getsize(video_file)/1000000.0
        print 'Requested AlarmVerification on file {0} ({1} Mb)'.format(video_file, file_size)

        url = "{0}/{1}".format(self.base_url, self.end_point)
        files = {'video': open("{0}".format(video_file))}
        r = requests.post(url, headers=self.header, files=files,  allow_redirects=True)

        # while the task is not complete, lets keep checking it
        task = r.json()['task']
        if self.verbose:
            print task

        while not task['complete']:
            time.sleep(0.5)
            job_id = task['job_id']
            url = "{0}/{1}/{2}".format(self.base_url, self.end_point, job_id)
            response = requests.get(url, headers=self.header, allow_redirects=True)
            task = response.json()['task']
            if self.verbose:
                print task

        print ' - probability of alarm {}%'.format(task['probability'])
        if download:
            self.download_file(task['results_video'])
        return task


class FaceDetect(VideoAIUser):

    def __init__(self, key_file = '', verbose=False):
        super(FaceDetect, self).__init__(key_file=key_file, verbose=verbose)
        self.end_point = 'face_detect'

    def apply(self, video_file, download=True):

        file_size = os.path.getsize(video_file)/1000000.0
        print 'Requested FaceDetect on file {0} ({1} Mb)'.format(video_file, file_size)

        url = "{0}/{1}".format(self.base_url, self.end_point)
        files = {'video': open("{0}".format(video_file))}
        r = requests.post(url, headers=self.header, files=files,  allow_redirects=True)

        # while the task is not complete, lets keep checking it
        task = r.json()['task']
        if self.verbose:
            print task

        while not task['complete']:
            time.sleep(0.5)
            job_id = task['job_id']
            url = "{0}/{1}/{2}".format(self.base_url, self.end_point, job_id)
            response = requests.get(url, headers=self.header, allow_redirects=True)
            task = response.json()['task']
            if self.verbose:
                print task

        if download:
            self.download_file(task['results_video'])
            self.download_file(task['results_xml'])
        return task