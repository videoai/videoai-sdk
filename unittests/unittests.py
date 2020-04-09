from videoai import FaceLog, FaceLogImage

import unittest
import os

face_detect_data_dir = os.path.join('../..', 'test-data', 'FaceDetector')
face_recognition_data_dir = os.path.join('../..', 'test-data', 'FaceRecognition')


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
            face_log = FaceLog.create(verbose=True)
            task = face_log.apply(video_file=video_path,
                                  max_frames=test_data.max_frames,
                                  min_size=test_data.min_size)
            return task

        # Test on some known videos
        def test_face_log(self):
            print("Testing face log...")

            test_data = [
                        TestFaceLog.TestData(video_file='busy_office.mkv', frames=103, max_frames=0, number_of_sightings=3, min_size=40),
                        TestFaceLog.TestData(video_file='kieron01.mkv', frames=105, max_frames=0, number_of_sightings=1, min_size=80),
            ]

            for this_test in test_data:
                print("** Testing {0} **".format(this_test.video_file))
                response = self.do_face_log(this_test)
                self.assertEqual(response['status'], 'success')
                task = response['task']
                self.assertTrue(task['analytic'], "face_log")
                self.assertTrue(task['complete'])
                self.assertEqual(task['number_of_sightings'], this_test.number_of_sightings)
                if this_test.max_frames == 0:
                    this_test.max_frames = this_test.frames
                self.assertEqual(task['frames_processed'], this_test.max_frames)


class TestFaceLogImage(unittest.TestCase):

        # Do the actual alarm verification
        def do_face_log_image(self, image_file):

            face_log_image = FaceLogImage.create(verbose=True)
            image_path = os.path.join(face_detect_data_dir, image_file)
            task = face_log_image.apply(image_path, min_size=40)
            return task

        # Test on some known videos
        def test_face_log(self):
            print("Testing face detection...")

            test_data = { 'group.jpg': 16,
                          'KaliningradFaces.jpg': 48}

            for key, value in test_data.items():
                print("** Testing {0} with expected result {1} **".format(key, value))
                response = self.do_face_log_image(key)
                self.assertEqual(response['status'], 'success')
                task = response['task']
                print(task)
                self.assertTrue(task['analytic'], "face_log_image")
                self.assertTrue(task['complete'])
                self.assertEqual(task['number_of_sightings'], value)


if __name__ == '__main__':
    unittest.main()
