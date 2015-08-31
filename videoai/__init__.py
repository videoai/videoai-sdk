import os
import configparser
import base64
import requests
import time
from os.path import expanduser

class VideoAIUser(object):

    def __init__(self, key_file='', verbose=False):
        if not key_file:
            home = expanduser("~")
            key_file = os.path.join(home, '.videoai')
        config = configparser.ConfigParser()
        config.read(key_file)
        keys = config['videoai.net']
        apiKey = "{0}:{1}".format(keys['apiKey_id'], keys['apiKey_secret'])
        basic_auth_header = "Basic {0}".format(base64.b64encode(apiKey))
        self.header = {'Authorization': basic_auth_header}
        #self.base_url = "https://api.videoai.net"
        self.verbose = verbose
        self.base_url = "http://192.168.90.53:5000"
        #self.base_url = "http://54.195.251.39:5000"
        self.end_point = ''

    def wait(self, task):
        url = "{0}/{1}/{2}".format(self.base_url, self.end_point, task['job_id'])
        while not task['complete']:
            time.sleep(0.5)
            r = requests.get(url, headers=self.header, allow_redirects=True)
            if r.json()['status'] != 'success':
                raise Exception("Polling failed: {}". format(r.json()['message']))
            task = r.json()['task']
            if self.verbose:
                print task

        return task

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

    def tasks(self):
        '''
        Get a list of all tasks
        :return:
        '''
        url = "{0}/task".format(self.base_url)
        r = requests.get(url, headers=self.header, allow_redirects=True)
        return r.json()

    def task(self, job_id):
        '''
        Get a specific task
        :return:
        '''
        url = "{0}/{1}/{2}".format(self.base_url, self.end_point, job_id)
        r = requests.get(url, headers=self.header, allow_redirects=True)
        return r.json()


class KamCheck(VideoAIUser):

    def __init__(self, key_file = '', verbose=False):
        super(KamCheck, self).__init__(key_file=key_file, verbose=verbose)
        self.end_point = 'kamcheck'

    def request(self, image_file, video_file):

        image_file_size = os.path.getsize(image_file)/1000000.0
        video_file_size = os.path.getsize(video_file)/1000000.0
        print 'Requested KamCheck on image {0} ({1} Mb) and video {2} ({3} Mb)'.format(image_file, image_file_size, video_file, video_file_size)
        url = "{0}/{1}".format(self.base_url, self.end_point)
        files = {'image': open("{0}".format(image_file)),
                 'video': open("{0}".format(video_file))
        }
        r = requests.post(url, headers=self.header, files=files,  allow_redirects=True)

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("KamCheck request failed: {}". format(r.json()['message']))

        if self.verbose:
            print r.text

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


class AlarmVerification(VideoAIUser):

    def __init__(self, key_file = '', verbose=False):
        super(AlarmVerification, self).__init__(key_file=key_file, verbose=verbose)
        self.end_point = 'alarm_verification'

    def request(self, video_file):
        file_size = os.path.getsize(video_file)/1000000.0
        print 'Requested AlarmVerification on file {0} ({1} Mb)'.format(video_file, file_size)

        url = "{0}/{1}".format(self.base_url, self.end_point)
        files = {'video': open("{0}".format(video_file))}
        r = requests.post(url, headers=self.header, files=files,  allow_redirects=True)

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Alarm Verification request failed: {}". format(r.json()['message']))

        if self.verbose:
            print r.text

        return r.json()['task']

    def apply(self, video_file, download=True, wait_until_finished=True):

        # do initial request
        task = self.request(video_file)

        print 'wait...'
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


class FaceDetectImage(VideoAIUser):

    def __init__(self, key_file='', verbose=False):
        super(FaceDetectImage, self).__init__(key_file=key_file, verbose=verbose)
        self.end_point = 'face_detect_image'

    def request(self, image_file, blur, min_size):

        file_size = os.path.getsize(image_file)/1000000.0
        print 'Requested FaceDetectImage on {0} ({1} Mb)'.format(image_file, file_size)
        data = {'blur': blur, 'min_size': min_size}

        url = "{0}/{1}".format(self.base_url, self.end_point)

        files = {'image': open("{0}".format(image_file))}
        r = requests.post(url, headers=self.header, files=files,  data=data, allow_redirects=True)

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Face Detect request failed: {}". format(r.json()['message']))

        # while the task is not complete, lets keep checking it
        task = r.json()['task']
        if self.verbose:
            print r.text

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

    def __init__(self, key_file = '', verbose=False):
        super(FaceDetect, self).__init__(key_file=key_file, verbose=verbose)
        self.end_point = 'face_detect'

    def request(self, video_file, blur=0, start_frame=0, max_frames=0, min_size=30):

        file_size = os.path.getsize(video_file)/1000000.0
        print 'Requested FaceDetect on video {0} ({1} Mb)'.format(video_file, file_size)
        data = {'blur': blur, 'start_frame': start_frame, 'max_frames': max_frames, 'min_size': min_size}

        url = "{0}/{1}".format(self.base_url, self.end_point)
        files = {'video': open("{0}".format(video_file))}

        r = requests.post(url, headers=self.header, files=files,  data=data, allow_redirects=True)

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("Face Detect request failed: {}". format(r.json()['message']))

        # while the task is not complete, lets keep checking it
        task = r.json()['task']

        if self.verbose:
            print task

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


class FaceLog(VideoAIUser):

    def __init__(self, key_file = '', verbose=False):
        super(FaceLog, self).__init__(key_file=key_file, verbose=verbose)
        self.end_point = 'face_log'

    def request(self, video_file, gender=0, start_frame=0, max_frames=0, min_size=30, min_certainty=1):

        file_size = os.path.getsize(video_file)/1000000.0
        print 'Requested FaceLog on video {0} ({1} Mb)'.format(video_file, file_size)
        data = {'gender': gender, 'start_frame': start_frame, 'max_frames': max_frames, 'min_size': min_size, 'min_certainty': min_certainty}

        url = "{0}/{1}".format(self.base_url, self.end_point)

        files = {'video': open("{0}".format(video_file))}

        r = requests.post(url, headers=self.header, files=files,  data=data, allow_redirects=True)

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("face_log request failed: {}". format(r.json()['message']))

        # while the task is not complete, lets keep checking it
        task = r.json()['task']
        if self.verbose:
            print task

        return task

    def apply(self, video_file, download=True, gender=0, start_frame=0, max_frames=0, min_size=30, min_certainty=1.0, wait_until_finished=True):

        task = self.request(video_file, gender=gender, start_frame=start_frame, max_frames=max_frames, min_size=min_size, min_certainty=min_certainty)

        if not wait_until_finished:
            return task

        task = self.wait(task)

        if not task['success']:
            print 'Failed FaceLog: {0}'.format(task['message'])
            return task

        if download:
            self.download_file(task['results_video'])
            self.download_file(task['results_xml'])

            for sighting in task['sightings']:
                self.download_file(sighting['thumbnail'])

        return task


class SafeZone2d(VideoAIUser):

    def __init__(self, key_file = '', verbose=False):
        super(SafeZone2d, self).__init__(key_file=key_file, verbose=verbose)
        self.end_point = 'safezone_2d'

    def request(self, video_file, start_frame=0, max_frames=0):

        file_size = os.path.getsize(video_file)/1000000.0
        print 'Requested SafeZone2d on video {0} ({1} Mb)'.format(video_file, file_size)
        data = {'start_frame': start_frame, 'max_frames': max_frames}

        url = "{0}/{1}".format(self.base_url, self.end_point)
        files = {'video': open("{0}".format(video_file))}

        r = requests.post(url, headers=self.header, files=files,  data=data, allow_redirects=True)

        if r.json()['status'] != 'success':
            print r.text
            raise Exception("safezone_2d request failed: {}". format(r.json()['message']))

        # while the task is not complete, lets keep checking it
        task = r.json()['task']
        if self.verbose:
            print task

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


