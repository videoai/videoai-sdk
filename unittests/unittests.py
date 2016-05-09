from twisted.conch.test.test_transport import factory
from videoai import KamCheck, AlarmVerification, FaceDetect, FaceDetectImage, FaceLog, FaceLogImage, SafeZone2d, Enhance 

import unittest
import base64
import requests
import os
import json
import time

kamcheck_data_dir = os.path.join('../..', 'test-data', 'KamCheck')
alarm_verification_data_dir = os.path.join('../..', 'test-data', 'AlarmVerification')
face_detect_data_dir = os.path.join('../..', 'test-data', 'FaceDetector')
face_recognition_data_dir = os.path.join('../..', 'test-data', 'FaceRecognition')
safezone_data_dir = os.path.join('../..', 'test-data', 'SafeZone')
enhance_data_dir = os.path.join('../..', 'test-data', 'Enhance')
host="https://api.videoai.net"
#host = "http://localhost:5000"
#host = "http://52.49.251.87"

class TestKamCheck(unittest.TestCase):

        def do_kam_check(self, image_file, video_file):

            image_path = os.path.join(kamcheck_data_dir, image_file)
            video_path = os.path.join(kamcheck_data_dir, video_file)

            kamcheck = KamCheck(host=host)
            task = kamcheck.apply(image_file=image_path, video_file=video_path)
            print task
            return task


        def test_kam_check(self):
            print "Testing kam check..."
    
            task = self.do_kam_check('parkingRef.png', 'parking.avi')
            self.assert_(task['analytic'], "kamcheck")        
            self.assertTrue(task['complete'])
            self.assertEqual(task['probability'], 0)
        
            task = self.do_kam_check('kamcheck01.jpg', 'kamcheck01.avi')
            self.assert_(task['analytic'], "kamcheck")        
            self.assertTrue(task['complete'])
            self.assertEqual(task['probability'], 0)

            task = self.do_kam_check('kamcheck02.jpg', 'kamcheck02.avi')
            self.assert_(task['analytic'], "kamcheck")        
            self.assertTrue(task['complete'])
            self.assertEqual(task['probability'], 100)
            
            task = self.do_kam_check('kamcheck03.jpg', 'kamcheck03.avi')
            self.assert_(task['analytic'], "kamcheck")        
            self.assertTrue(task['complete'])
            self.assertEqual(task['probability'], 100)
            
            
            # what happens when someone gets them muddled up
            with self.assertRaises(Exception):
                task = self.do_kam_check('kamcheck01.avi', 'kamcheck01.jpg')


class TestAlarmVerification(unittest.TestCase):

        # Do the actual alarm verification
        def do_alarm_verification(self, video_file):
            video_path = os.path.join(alarm_verification_data_dir, video_file)
            alarm_verification = AlarmVerification(host=host, verbose=True)
            task = alarm_verification.apply(video_file=video_path)
            print task
            return task

        # Test on some known videos
        def test_alarm_verification(self):
            print "Testing alarm verification..."

            #test_data = { 'Alarm.mpg':100, 'NoAlarm.mpg':2, '1.avi':100, '2.avi':100 }
            test_data = { 'intrusion.avi':100, 'officeEntry.mp4':100 }
            for key, value in test_data.iteritems():
                print "** Testing {0} with expected result {1} **".format(key, value)
                task = self.do_alarm_verification(key)
                self.assert_(task['analytic'], "alarm_verification")
                self.assertTrue(task['complete'])
                self.assertEqual(task['probability'], value)

class TestFaceDetectImage(unittest.TestCase):

        # Do the actual alarm verification
        def do_face_detect(self, image_file):

            face_detect_image = FaceDetectImage(host=host)
            image_path = os.path.join(face_detect_data_dir, image_file)
            task = face_detect_image.apply(image_path)
            return task

        # Test on some known videos
        def test_face_detect(self):
            print "Testing face detection..."

            test_data = { 'group.jpg':16 , 'monifiethGIRLSpresentation2009-748708.jpg':16, 'KaliningradFaces.jpg':43 }

            for key, value in test_data.iteritems():
                print "** Testing {0} with expected result {1} **".format(key, value)
                task = self.do_face_detect(key)
                self.assert_(task['analytic'], "face_detect_image")
                self.assertTrue(task['complete'])
                self.assertEqual(task['number_of_faces'], value)


class TestFaceDetect(unittest.TestCase):

        class TestData:
            def __init__(self, video_file, frames, max_frames, number_of_faces):
                self.video_file = video_file
                self.frames = frames
                self.max_frames = max_frames
                self.number_of_faces = number_of_faces
                self.verbose = True

        # Do the actual alarm verification
        def do_face_detect(self, test_data):
            video_path = os.path.join(face_detect_data_dir, test_data.video_file)
            face_detect = FaceDetect(host=host, verbose=test_data.verbose)
            task = face_detect.apply(video_file=video_path, max_frames=test_data.max_frames)
            return task

        # Test on some known videos
        def test_face_detect(self):
            print "Testing face detection..."
            #TestFaceDetect.TestData('demoFaceDetect.avi', 1138, 200, 54),
            test_data = [
                        TestFaceDetect.TestData('officeEntry.mp4', frames=81, max_frames=0, number_of_faces=5),
                        TestFaceDetect.TestData('officeEntry.mp4', frames=81, max_frames=20, number_of_faces=0)
            ]

            for this_test in test_data:
                print "** Video File {0} w **".format(this_test.video_file)
                task = self.do_face_detect(this_test)
                self.assert_(task['analytic'], "face_detect")
                self.assertTrue(task['complete'])
                self.assertEqual(task['number_of_faces'], this_test.number_of_faces)
                if this_test.max_frames == 0:
                    this_test.max_frames = this_test.frames
                self.assertEqual(task['frames_processed'], this_test.max_frames)


class TestFaceLog(unittest.TestCase):

        class TestData:
            def __init__(self, video_file, frames, max_frames, number_of_sightings, min_size=80):
                self.video_file = video_file
                self.frames = frames
                self.max_frames = max_frames
                self.min_size = min_size
                self.number_of_sightings = number_of_sightings
                self.verbose = True

        # Do the actual alarm verification
        def do_face_log(self, test_data):
            video_path = os.path.join(face_recognition_data_dir, test_data.video_file)
            face_log = FaceLog(host=host, verbose=True)
            task = face_log.apply(video_file=video_path, max_frames=test_data.max_frames, min_size=test_data.min_size)
            return task

        # Test on some known videos
        def test_face_log(self):
            print "Testing face log..."

            test_data = [
                        TestFaceLog.TestData(video_file='busy_office.mkv', frames=103, max_frames=0, number_of_sightings=3, min_size=40),
                        TestFaceLog.TestData(video_file='kieron01.mkv', frames=105, max_frames=0, number_of_sightings=1, min_size=80),
            ]

            for this_test in test_data:
                print "** Testing {0} **".format(this_test.video_file)
                task = self.do_face_log(this_test)
                self.assert_(task['analytic'], "face_detect")
                self.assertTrue(task['complete'])
                self.assertEqual(task['number_of_sightings'], this_test.number_of_sightings)
                if this_test.max_frames == 0:
                    this_test.max_frames = this_test.frames
                self.assertEqual(task['frames_processed'], this_test.max_frames)


class TestFaceLogImage(unittest.TestCase):

        # Do the actual alarm verification
        def do_face_log(self, image_file):

            face_log_image = FaceLogImage(host=host, verbose=True)
            image_path = os.path.join(face_detect_data_dir, image_file)
            task = face_log_image.apply(image_path, min_size=40)
            return task

        # Test on some known videos
        def test_face_log(self):
            print "Testing face detection..."

            test_data = { 'group.jpg':15 }

            for key, value in test_data.iteritems():
                print "** Testing {0} with expected result {1} **".format(key, value)
                task = self.do_face_log(key)
                self.assert_(task['analytic'], "face_log_image")
                self.assertTrue(task['complete'])
                self.assertEqual(task['number_of_faces'], value)


class TestSafeZone2d(unittest.TestCase):

        class TestData:
            def __init__(self, video_file, frames, max_frames):
                self.video_file = video_file
                self.frames = frames
                self.max_frames = max_frames
                self.verbose = True

        # Do the actual alarm verification
        def do_safezone_2d(self, test_data):
            video_path = os.path.join(safezone_data_dir, test_data.video_file)
            safezone_2d = SafeZone2d(host=host, verbose=True)
            task = safezone_2d.apply(video_file=video_path, max_frames=test_data.max_frames)
            return task

        # Test on some known videos
        def test_safezone2d(self):
            print "Testing SafeZone2d..."

            test_data = [
                TestSafeZone2d.TestData(video_file='vegetation.avi', frames=668, max_frames=0),
            ]

            for this_test in test_data:
                print "** Testing {0} **".format(this_test.video_file)
                task = self.do_safezone_2d(this_test)
                self.assert_(task['analytic'], "safezone_2d")
                self.assertTrue(task['complete'])
                if this_test.max_frames == 0:
                    this_test.max_frames = this_test.frames
                self.assertEqual(task['frames_processed'], this_test.max_frames)

class TestEnhance(unittest.TestCase):

        class TestData:
            def __init__(self, video_file, algorithm, frames, max_frames):
                self.video_file = video_file
                self.algorithm = algorithm
                self.frames = frames
                self.max_frames = max_frames
                self.verbose = True

        # Do the actual alarm verification
        def do_enhance(self, test_data):
            video_path = os.path.join(enhance_data_dir, test_data.video_file)
            enhance = Enhance(host=host, verbose=True, algorithm=test_data.algorithm)
            task = enhance.apply(video_file=video_path, max_frames=test_data.max_frames)
            return task

        # Test on some known videos
        def test_enhance(self):
            print "Testing Enhance..."

            test_data = [
                TestEnhance.TestData(video_file='vegetation.avi', algorithm='stabilisation', frames=668, max_frames=0),
                TestEnhance.TestData(video_file='vegetation.avi', algorithm='lace', frames=668, max_frames=0),
            ]

            for this_test in test_data:
                print "** Testing {0} **".format(this_test.video_file)
                task = self.do_enhance(this_test)
                self.assert_(task['algorithm'], this_test.algorithm)
                self.assertTrue(task['complete'])
                if this_test.max_frames == 0:
                    this_test.max_frames = this_test.frames
                self.assertEqual(task['frames_processed'], this_test.max_frames)


if __name__ == '__main__':
    unittest.main()
