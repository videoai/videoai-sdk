from videoai.recognition import Recognition
from videoai import FaceLog

import unittest
import os
import uuid
import json

data_dir = os.path.join('../..', 'test-data', 'FaceRecognition')
SIGHTINGS_FILE = 'sightings.txt'

class TestEnrolSubjects(unittest.TestCase):

    def setUp(self):
        self.face_log = FaceLog()
        self.recognition = Recognition()

    def test_face_log(self):
        '''
        This onlyt gets run if we do not have a valid sightings file
        which contains the name and a sighting id
        :return:
        '''
        # If we have sightings file, lets return
        if os.path.isfile(SIGHTINGS_FILE):
            return

        # lets delete any subjects we may already have
        subjects = self.recognition.list_subjects()
        for subject in subjects:
            print 'Going to delete {0}'.format(subject['subject_id'])
            deleted_id = self.recognition.delete_subject(subject['subject_id'])
            self.assertEqual(subject['subject_id'], deleted_id)


        # these are the video files
        video_files = {
            'Alberto': '{}/Subjects/Alberto.mov'.format(data_dir),
            'Baris': '{}/Subjects/Baris.mov'.format(data_dir),
            'Fred': '{}/Subjects/Fred.mov'.format(data_dir),
            'Kjetil': '{}/Subjects/Kjetil.mov'.format(data_dir),
            'Laurent': '{}/Subjects/Laurent.mov'.format(data_dir),
            'Marie-Claude': '{}/Subjects/Marie-Claude.mov'.format(data_dir),
            'Olivier': '{}/Subjects/Olivier.mov'.format(data_dir)
        }
        video_files1 = {
            'Alberto': '{}/Subjects/Alberto.mov'.format(data_dir),
        }

        # lets run face-log and get the sightings, enrol the subjects
        sighting_list = {}
        for name, video_file in video_files.iteritems():
            task = self.face_log.apply(video_file=video_file, download=False, gender=True, max_frames=10)
            self.assertTrue(task['success'])
            sightings = task['sightings']
            self.assertEqual(1, len(sightings))
            subject_id = self.recognition.create_subject(name=name)
            sighting_list[subject_id] = sightings[0]['sighting_id']
            print '{} {} {}'.format(subject_id, name, sightings[0]['sighting_id'])

        # save to a file to do some things with
        with open(SIGHTINGS_FILE, 'w') as f:
            f.write(json.dumps(sighting_list))

    def test_enrol(self):
        # check we have a sightings file
        self.assertTrue(os.path.isfile(SIGHTINGS_FILE))

        with open(SIGHTINGS_FILE, 'r') as f:
            sightings = json.load(f)

        for subject_id, sighting_id in sightings.iteritems():
            print subject_id, subject_id
            self.recognition.add_sighting_to_subject(sighting_id=sighting_id, subject_id=subject_id)



class TestSubject(unittest.TestCase):

        class TestData:
            def __init__(self, name, user_data):
                self.name = name
                self.user_data = user_data
                self.verbose = True

        def setUp(self):
            self.recognition = Recognition()
            self.face_log = FaceLog()

        # Test on some known videos
        def create_subjects(self):
            print "Creating some subjects"

            test_data = [
                        TestSubject.TestData(name='Kieron', user_data='user data'),
                        TestSubject.TestData(name='Katie', user_data='a lady')
            ]

            for this_test in test_data:
                print "** Testing {0} **".format(this_test.name)
                subject = self.recognition.create_subject(name=this_test.name, user_data=this_test.user_data)
                print 'created subject {name} {subject_id}'.format(name=subject['name'], subject_id=subject['subject_id'])
                self.assertIsNotNone(subject['subject_id'])

        def list_subjects(self):
            print "List all the subjects"

            subjects = self.recognition.list_subjects()

            self.assertIsNotNone(subjects)

            for subject in subjects:
                print '{0} has id {1} and thumbnail {2}'.format(subject['name'], subject['subject_id'], subject['thumbnail'])
                self.recognition.download_with_authentication(subject['thumbnail'], '{}.jpg'.format(subject['subject_id']))

        def delete_subjects(self):
            subjects = self.recognition.list_subjects()
            for subject in subjects:
                print 'Going to delete {0}'.format(subject['subject_id'])
                deleted_id = self.recognition.delete_subject(subject['subject_id'])
                self.assertEqual(subject['subject_id'], deleted_id)


class TestTag(unittest.TestCase):

        class TestData:
            def __init__(self, name):
                self.name = name
                self.verbose = True

        def setUp(self):
            self.recognition = Recognition()

        def create_tags(self):
            print "Creating some watchlists"

            test_data = [
                        TestTag.TestData(name='Blacklist'),
                        TestTag.TestData(name='Whitelist'),
                        TestTag.TestData(name='Office')
            ]

            for this_test in test_data:
                print "** Testing {0} **".format(this_test.name)
                tag = self.recognition.create_tag(name=this_test.name)
                print 'created tag {name} {tag_id}'.format(name=tag['name'], tag_id=tag['watchlist_id'])
                self.assertIsNotNone(tag['tag_id'])

        def list_tags(self):
            print "List all the watchlists"

            tags = self.recognition.list_tags()

            self.assertIsNotNone(tags)

            for tag in tags:
                print '{0} has id {1}'.format(tag['name'], tag['tag_id'])

        def delete_tags(self):
            tags = self.recognition.list_tags()
            for tag in tags:
                print 'Going to delete {0}'.format(tag['tag_id'])
                deleted_id = self.recognition.delete_tag(tag['tag_id'])
                self.assertEqual(tag['tag_id'], deleted_id)


if __name__ == '__main__':
    unittest.main()
