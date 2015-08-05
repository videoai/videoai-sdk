from twisted.conch.test.test_transport import factory
from videoai import KamCheck, AlarmVerification, FaceDetect, FaceDetectImage, FaceLog

import unittest
import base64
import requests
import os
import json
import time

kamcheck_data_dir = os.path.join('..', 'test-data', 'KamCheck')
alarm_verification_data_dir = os.path.join('..', 'test-data', 'AlarmVerification')
face_detect_data_dir = os.path.join('..', 'test-data', 'FaceDetector')


    
class TestKamCheck(unittest.TestCase):

        def do_kam_check(self, image_file, video_file):

            image_path = os.path.join(kamcheck_data_dir, image_file)
            video_path = os.path.join(kamcheck_data_dir, video_file)

            kamcheck = KamCheck()
            task = kamcheck.apply(image_file=image_path, video_file=video_path)
            print task
            return task


        def test_kam_check(self):
            print "Testing kam check..."
    
            task = self.do_kam_check('parkingRef.png', 'parking.avi')
            self.assert_(task['analytic'], "kamcheck")        
            self.assertTrue(task['complete'])
            self.assertEqual(task['probability'], 0)
        
            task = self.do_kam_check('PTZRef.png', 'PTZ.avi')
            self.assert_(task['analytic'], "kamcheck")        
            self.assertTrue(task['complete'])
            self.assertEqual(task['probability'], 100)

            # what happens when someone gets them muddled up
            with self.assertRaises(Exception):
                task = self.do_kam_check('PTZ.avi', 'PTZRef.png')

class TestAlarmVerification(unittest.TestCase):

        # Do the actual alarm verification
        def do_alarm_verification(self, video_file):
            video_path = os.path.join(alarm_verification_data_dir, video_file)
            alarm_verification = AlarmVerification()
            task = alarm_verification.apply(video_file=video_path)
            print task
            return task

        # Test on some known videos
        def test_alarm_verification(self):
            print "Testing alarm verification..."

            #test_data = { 'Alarm.mpg':100, 'NoAlarm.mpg':2, '1.avi':100, '2.avi':100 }
            test_data = { 'intrusion.avi':100, 'officeEntry.mp4':100, 'windy.avi':100 }
            for key, value in test_data.iteritems():
                print "** Testing {0} with expected result {1} **".format(key, value)
                task = self.do_alarm_verification(key)
                self.assert_(task['analytic'], "alarm_verification")
                self.assertTrue(task['complete'])
                self.assertEqual(task['probability'], value)

class TestFaceDetectImage(unittest.TestCase):

        # Do the actual alarm verification
        def do_face_detect(self, image_file):

            face_detect_image = FaceDetectImage(verbose=True)
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

        # Do the actual alarm verification
        def do_face_detect(self, video_file, max_frames):
            video_path = os.path.join(face_detect_data_dir, video_file)
            face_detect = FaceDetect()
            task = face_detect.apply(video_file=video_path, max_frames=max_frames)
            return task

        # Test on some known videos
        def test_face_detect(self):
            print "Testing face detection..."

            #test_data = { 'tracking.mov': [25, 18],  'demoFaceDetect.avi': [200, 57], 'glasgow.mpg': [50, 0] }
            test_data = { 'demoFaceDetect.avi': [50, 57] }

            for key, value in test_data.iteritems():
                print "** Testing {0} with expected result {1} **".format(key, value)
                task = self.do_face_detect(key, value[0])
                self.assert_(task['analytic'], "face_detect")
                self.assertTrue(task['complete'])
                self.assertEqual(task['number_of_faces'], value[1])


if __name__ == '__main__':
    unittest.main()
