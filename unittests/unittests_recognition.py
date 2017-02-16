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
        self.face_log = FaceLog.create()
        self.recognition = Recognition.create()

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
        json_data = self.recognition.list_subjects()
        subjects = json_data['data']['subjects']
        for subject in subjects:
            print 'Going to delete {0}'.format(subject['subject_id'])
            deleted_id = self.recognition.delete_subject(subject['subject_id'])
            self.assertEqual(subject['subject_id'], deleted_id)


        # these are the video files
        video_files = {
            'Baris': '{}/Baris.mov'.format(data_dir),
            'Kjetil': '{}/Kjetil.mov'.format(data_dir),
            'Laurent': '{}/Laurent.mov'.format(data_dir),
            'Marie-Claude': '{}/Marie-Claude.mov'.format(data_dir),
            'Olivier': '{}/Olivier.mov'.format(data_dir)
        }

        # lets run face-log and get the sightings, enrol the subjects
        sighting_list = {}
        for name, video_file in video_files.iteritems():
            json_data = self.face_log.apply(video_file=video_file, download=False, max_frames=10)
            print json.dumps(json_data, indent=4, sort_keys=True)
            sightings = json_data['task']['sightings']
            self.assertEqual(1, len(sightings))
            cs_json_data = self.recognition.create_subject(name=name)
            subject_id = cs_json_data['data']['subject']['subject_id']
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
            def __init__(self, name):
                self.name = name
                self.verbose = True

        def setUp(self):
            self.recognition = Recognition.create()
            self.face_log = FaceLog.create()

        # Test on some known videos
        def create_subjects(self):
            print "Creating some subjects"

            test_data = [
                        TestSubject.TestData(name='Kieron'),
                        TestSubject.TestData(name='Katie')
            ]

            json_response = self.recognition.list_tags()
            tags = Tags.from_json(json_response)

            print tags.to_json()

            for this_test in test_data:
                print "** Testing {0} **".format(this_test.name)
                json_data = self.recognition.create_subject(name=this_test.name)
                print json_data
                #print 'created subject {name} {subject_id}'.format(name=subject['name'], subject_id=subject[
                # 'subject_id'])
                #self.assertIsNotNone(subject['subject_id'])

        def list_subjects(self):
            print "List all the subjects"

            json_data = self.recognition.list_subjects()
            self.assertIsNotNone(json_data)
            self.assertEqual(json_data['status'], 'success')
            subjects = json_data['data']['subjects']
            print json.dumps(subjects, indent=4, sort_keys=True)

            for subject in subjects:
                print '{0} has id {1} and thumbnail {2}'.format(subject['name'], subject['subject_id'], subject['thumbnail'])
                self.recognition.subject_thumbnail(subject['subject_id'])

        def delete_subjects(self):
            json_data = self.recognition.list_subjects()
            self.assertIsNotNone(json_data)
            self.assertEqual(json_data['status'], 'success')
            subjects = json_data['data']['subjects']
            for subject in subjects:
                print 'Going to delete {0}'.format(subject['subject_id'])
                json_data = self.recognition.delete_subject(subject['subject_id'])
                self.assertIsNotNone(json_data)
                self.assertEqual(json_data['status'], 'success')


class TestTag(unittest.TestCase):

        class TestData:
            def __init__(self, name):
                self.name = name
                self.verbose = True

        def setUp(self):
            self.recognition = Recognition.create()

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
