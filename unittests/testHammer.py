from videoai import KamCheck, AlarmVerification, FaceDetect, FaceDetectImage, FaceLog, SafeZone2d

from multiprocessing import Pool

import unittest
import os

kamcheck_data_dir = os.path.join('../..', 'test-data', 'KamCheck')
alarm_verification_data_dir = os.path.join('../..', 'test-data', 'AlarmVerification')
face_detect_data_dir = os.path.join('../..', 'test-data', 'FaceDetector')
safezone_data_dir = os.path.join('../..', 'test-data', 'SafeZone')
host = "http://api2"
#host = 'http://localhost:5000'

# Some constants for test
POOL_SIZE = 4
EXTEND_BY = 1


def do_alarm_verification(video_file):
    video_path = os.path.join(alarm_verification_data_dir, video_file)
    alarm_verification = AlarmVerification(host=host)
    task = alarm_verification.apply(video_file=video_path, download=False)
    print task
    return task['probability']


def do_face_detect_image(image_file):
    face_detect_image = FaceDetectImage(host=host)
    image_path = os.path.join(face_detect_data_dir, image_file)
    task = face_detect_image.apply(image_path, download=False)
    print task
    return task['number_of_faces']


def do_face_detect(video_file):
    face_detect = FaceDetect(host=host)
    video_path = os.path.join(face_detect_data_dir, video_file)
    task = face_detect.apply(video_path, download=False)
    print task
    return task['number_of_faces']


def do_face_log(video_file):
    face_log = FaceLog(host=host)
    video_path = os.path.join(face_detect_data_dir, video_file)
    task = face_log.apply(video_path, download=False)
    print task
    return task['message']


def extend(data, results, by):
    test_data = []
    expected_results = []
    for i in range(0, by):
        test_data += data
        expected_results += results
    return test_data, expected_results


class TestAlarmVerification(unittest.TestCase):

    def test_alarm_verification(self):
        print "Testing Alarm Verification..."
        data = ['intrusion.avi', 'NoAlarm.mpg']
        results = [100, 2]
        test_data, expected_results = extend(data, results, EXTEND_BY)
        print test_data
        pool = Pool(POOL_SIZE)
        actual_results = pool.map(do_alarm_verification, test_data)
        print actual_results
        self.assertEqual(expected_results, actual_results)


class TestFaceDetectImage(unittest.TestCase):

    def test_face_detect_image(self):
        print "Testing Face Detect Image..."
        data = ['group.jpg', 'monifiethGIRLSpresentation2009-748708.jpg', 'KaliningradFaces.jpg']
        results = [16, 16, 43]
        test_data, expected_results = extend(data, results, EXTEND_BY)
        print test_data
        pool = Pool(POOL_SIZE)
        actual_results = pool.map(do_face_detect_image, test_data)
        print actual_results
        self.assertEqual(expected_results, actual_results)


class TestFaceDetect(unittest.TestCase):

    def test_face_detect(self):
        print "Testing Face Detect..."
        data = ['officeEntry.mp4', 'demoFaceDetect.avi']
        results = [5, 12]
        test_data, expected_results = extend(data, results, EXTEND_BY)
        print test_data
        pool = Pool(POOL_SIZE)
        actual_results = pool.map(do_face_detect, test_data)
        print actual_results
        self.assertEqual(expected_results, actual_results)


class TestFaceLog(unittest.TestCase):

    def test_face_log(self):
        print "Testing Face Log..."
        data = ['demoFaceDetect.avi', 'officeEntry.mp4']
        results = [u'Face log found 23 sightings, 50 tracks and 315 faces', u'Face log found 0 sightings, 2 tracks and 5 faces']
        test_data, expected_results = extend(data, results, EXTEND_BY)
        pool = Pool(POOL_SIZE)
        actual_results = pool.map(do_face_log, test_data)
        print actual_results
        self.assertEqual(expected_results, actual_results)


if __name__ == '__main__':
    unittest.main()
