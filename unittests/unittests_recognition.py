from videoai.recognition import Recognition

import unittest
import os
import uuid

face_detect_data_dir = os.path.join('..', 'test-data', 'FaceDetector')


class TestSubject(unittest.TestCase):

        class TestData:
            def __init__(self, name, user_data):
                self.name = name
                self.user_data = user_data
                self.verbose = True

        def setUp(self):
            self.recognition = Recognition()

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
                print '{0} has id {1}'.format(subject['name'], subject['subject_id'])

        def delete_subjects(self):
            subjects = self.recognition.list_subjects()
            for subject in subjects:
                print 'Going to delete {0}'.format(subject['subject_id'])
                deleted_id = self.recognition.delete_subject(subject['subject_id'])
                self.assertEqual(subject['subject_id'], deleted_id)


class TestWatchlist(unittest.TestCase):

        class TestData:
            def __init__(self, name):
                self.name = name
                self.verbose = True

        def setUp(self):
            self.recognition = Recognition()

        def create_watchlists(self):
            print "Creating some watchlists"

            test_data = [
                        TestWatchlist.TestData(name='Blacklist'),
                        TestWatchlist.TestData(name='Whitelist'),
                        TestWatchlist.TestData(name='Office')
            ]

            for this_test in test_data:
                print "** Testing {0} **".format(this_test.name)
                watchlist = self.recognition.create_watchlist(name=this_test.name)
                print 'created watchlist {name} {watchlist_id}'.format(name=watchlist['name'], watchlist_id=watchlist['watchlist_id'])
                self.assertIsNotNone(watchlist['watchlist_id'])

        def list_watchlists(self):
            print "List all the watchlists"

            watchlists = self.recognition.list_watchlists()

            self.assertIsNotNone(watchlists)

            for watchlist in watchlists:
                print '{0} has id {1}'.format(watchlist['name'], watchlist['watchlist_id'])

        def delete_watchlists(self):
            watchlists = self.recognition.list_watchlists()
            for watchlist in watchlists:
                print 'Going to delete {0}'.format(watchlist['watchlist_id'])
                deleted_id = self.recognition.delete_watchlist(watchlist['watchlist_id'])
                self.assertEqual(watchlist['watchlist_id'], deleted_id)



if __name__ == '__main__':
    unittest.main()
