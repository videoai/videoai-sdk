#!/bin/env
import os
from videoai import FaceLogImage, DeleteSubjects
from videoai.recognition import Recognition
from concurrent.futures import ThreadPoolExecutor
import json
import random
import time
from os import listdir
from os.path import isfile, join, splitext
import argparse
from addict import Dict
import pprint


pp = pprint.PrettyPrinter(indent=4)

def create_random_colour():
    r = lambda: random.randint(0, 255)
    colour = '#%02X%02X%02X' % (r(), r(), r())
    return colour

watchlist = [
    {'name': 'High Risk', 'colour': create_random_colour(), 'threshold': 0.55, 'top_n': 10},
    {'name': 'Staff', 'colour': create_random_colour(), 'threshold': 0.55, 'top_n': 10},
    {'name': 'Contractor', 'colour': create_random_colour(), 'threshold': 0.55, 'top_n': 10},
    {'name': 'Visitor', 'colour': create_random_colour(), 'threshold': 0.55, 'top_n': 10},
    {'name': 'Authorized', 'colour': create_random_colour(), 'threshold': 0.55, 'top_n': 10},
    {'name': 'Restricted', 'colour': create_random_colour(), 'threshold': 0.55, 'top_n': 10},
    {'name': 'Athlete', 'colour': create_random_colour(), 'threshold': 0.55, 'top_n': 10}
]



def timerfunc(func):
    """
    A timer decorator
    """
    def function_timer(*args, **kwargs):
        """
        A nested function for timing other functions
        """
        start = time.time()
        value = func(*args, **kwargs)
        end = time.time()
        runtime = end - start
        msg = "The runtime for {func} took {time} seconds to complete"
        print((msg.format(func=func.__name__,
                          time=runtime)))
        print(kwargs)
        return value
    return function_timer


def search_from_image(face_log_image, image_path, compare_threshold=0.55, top_n=1):

    try:
        if args.verbose:
            print('Searching from image {}'.format(image_path))

        if not os.path.exists(image_path):
            print("Image path does not exist {}".format(image_path))
            return False

        results = face_log_image.apply(image_file=image_path,
                                       compare_threshold=compare_threshold,
                                       top_n=top_n,
                                       recognition=True,
                                       download=False,
                                       wait_until_finished=True)
        return True
    except Exception as e:
        if args.verbose:
            pp.pprint(results)
        print('Exception caught {}: {}'.format(e, image_path))
        return False


def delete_subject(recognition, subject_id):
    return recognition.delete_subject(subject_id=subject_id)


def create_subject(recognition, name, watchlist):
    if args.verbose:
        print('Creating subject {} in watchlist {}'.format(name, watchlist))
    return recognition.create_subject(name=name, watchlist=watchlist)


def enrol_from_image(face_log_image, recognition, subject_id, image_path):
    try:
        if args.verbose:
            print('Enrolling subject {} from image {}'.format(subject_id, image_path))

        if not os.path.exists(image_path):
            print("Image path does not exist {}".format(image_path))
            return False

        results = face_log_image.apply(image_file=image_path,
                                       recognition=False,
                                       download=False,
                                       wait_until_finished=True)
        results = results['task']

        # if we find more than one face we are a bit screwed
        if results['number_of_sightings'] != 1:
            print('Too many of too few sightings {}'.format(results['number_of_sightings']))
            return False

        sighting = results['sightings'][0]

        # get info we need
        sighting_id = sighting['sighting_id']

        # if subject_id is None we just want to add a sighting
        results = recognition.add_sighting_to_subject(sighting_id=sighting_id,
                                                      subject_id=subject_id)
        return True
    except Exception as e:
        if args.verbose:
            pp.pprint(results)
        print(("Exception caught {}: {}".format(e, image_path)))
        return False


class ImportImageDir:

    def __init__(self):

        self.recognition = Recognition.create(key_file=args.key_file,
                                              authentication_server=args.authentication_server)

        self.delete_subjects = DeleteSubjects.create(key_file=args.key_file,
                                                     authentication_server=args.authentication_server)

        self.face_log_image = FaceLogImage.create(key_file=args.key_file,
                                                  authentication_server=args.authentication_server)

    def create_watchlists(self):
        success, content, headers = self.recognition.create_watchlist_for_unittest(watchlist=watchlist)
        if not success:
            raise Exception("Failed to call VideoAPI for watchlist creation")
        json_content = json.loads(content)

        if json_content['status'] != 'success':
            raise Exception("Problem creating unittest watchlist ({})".format(json_content))

    def get_subject_data(self, image_dir, number_of_subjects, max_faces_per_subject, subject_skip=0, id_list=None):
        if args.verbose:
            print("Importing {} subjects from image dir {}".format(number_of_subjects, image_dir))

        import_data = Dict()
        skipped = 0
        if id_list:
            with open(id_list, 'r') as id_file:
                for line in id_file:
                    if subject_skip > 0 and skipped < subject_skip:
                        skipped += 1
                        if args.verbose:
                            print('Skipping {}: {}'.format(skipped, qid))
                        continue
                    id = line.strip()
                    qid_image_dir = os.path.join(image_dir, qid)
                    if not os.path.exists(qid_image_dir):
                        print("Image Dir {} does not exist".format(qid_image_dir))
                        continue
                    files = [f for f in listdir(qid_image_dir) if isfile(join(qid_image_dir, f))]
                    import_data[id] = []
                    subject_images = 0
                    for file in files:
                        (image_name, ext) = splitext(file)
                        subject_images += 1
                        import_data[id].append(join(qid_image_dir, file))
                        if subject_images >= max_faces_per_subject > 0:
                            break
                    if args.verbose:
                        print("Subject {} Images {}".format(id, subject_images))
                    if len(import_data) >= number_of_subjects > 0:
                        break

        else:
            for root, subdirs, files in os.walk(image_dir):
                for subdir in subdirs:
                    subject_id = subdir
                    full_path = '{}/{}'.format(image_dir, subdir)
                    files = [f for f in listdir(full_path) if isfile(join(full_path, f))]
                    import_data[subject_id] = []
                    subject_images = 0
                    for file in files:
                        if subject_images >= int(max_faces_per_subject) > 0:
                            break
                        (image_name, ext) = splitext(file)
                        import_data[subject_id].append(join(full_path, file))
                        subject_images += 1
                    if args.verbose:
                        print("Subject {} Images {}".format(subject_id, subject_images))
                    if len(import_data) >= number_of_subjects > 0:
                        break

        number_of_images = sum(len(lst) for lst in import_data.values() )
        print("Number of subjects {} and images {}".format(len(import_data), number_of_images))
        return import_data

    def enrol_data(self, import_data):

        # get the watchlists
        permitted_watchlists = self.recognition.list_watchlists()
        if args.verbose:
            print(permitted_watchlists)
        permitted_watchlists = [x['id'] for x in permitted_watchlists['data']['watchlists']]

        # Make sure all subjects appear in database
        results = []
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            for subject, faces in import_data.items():
                results.append(executor.submit(create_subject, self.recognition, subject,
                                               random.choice(permitted_watchlists)))
            executor.shutdown(wait=True)

        # get a map of database id to videoai subject_id
        subjects = Dict()
        for result in results:
            subject = result.result()['data']['subject']
            subjects[subject['name']] = subject['subject_id']

        # Lets add faces to each subject using FaceLogImage
        number_of_faces = 0
        results = []
        with ThreadPoolExecutor(max_workers=args.workers) as executor:

            for subject_id, smartvisface_subject_id in subjects.items():
                images = import_data[subject_id]
                for image in images:
                    results.append(executor.submit(enrol_from_image,
                                                   self.face_log_image,
                                                   self.recognition,
                                                   smartvisface_subject_id,
                                                   image))
            executor.shutdown(wait=True)

        success = 0
        failure = 0
        for result in results:
            if result.result():
                success += 1
            else:
                failure += 1

        return success, failure

    def search_data(self, import_data):

        # Lets add faces to each subject using FaceLogImage
        number_of_faces = 0
        results = []
        with ThreadPoolExecutor(max_workers=args.workers) as executor:

            for subject, images in import_data.items():
                for image in images:
                    results.append(executor.submit(search_from_image,
                                                   self.face_log_image,
                                                   image))
            executor.shutdown(wait=True)

        success = 0
        failure = 0
        for result in results:
            if result.result():
                success += 1
            else:
                failure += 1

        return success, failure

    def delete_all_subjects(self):
        print("Deleting all subjects...")
        subjects = self.recognition.list_subjects()

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            results = []
            for subject in subjects['data']['subjects']:
                if args.verbose:
                    print('Deleting {}'.format(subject['subject_id']))
                this_result = executor.submit(delete_subject,
                                              self.recognition,
                                              subject['subject_id'])
                results.append(this_result)
            executor.shutdown(wait=True)
        print('Deleted {} subjects'.format(len(results)))

    @timerfunc
    def list_sightings(self):
        sightings = self.recognition.list_sightings(number_per_page=100000)
        print(sightings)



parser = argparse.ArgumentParser(description='Benchmark SmartVis Face Server',
                                 epilog='Digital Barriers.',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--image-dir', dest='image_dir', default='/mnt/image-db/FaceDatabase/DATABASE/images', help='The image directory.')
parser.add_argument('--id-list', dest='id_list', default=None, help='Get ids from this file.')
parser.add_argument('--workers', dest='workers', default=64, type=int, help='The number of worker threads.')
parser.add_argument('--key-file', dest='key_file', default=os.path.join(os.path.expanduser("~"), ".videoai"),  help='Path to your developer keys.')
parser.add_argument('--authentication-server', dest='authentication_server', default='http://192.168.86.197:10000', help='The authentication server to use.')
parser.add_argument('--create-watchlists', dest='create_watchlists', action='store_true', help='Create the watchlists.')
parser.add_argument('--delete-subjects', dest='delete_subjects', action='store_true', default=False, help='Delete all the subjects.')
parser.add_argument('--max-subjects', dest='max_subjects', type=int, default=-1, help='How many subjects to enrol.')
parser.add_argument('--subject_skip', dest='subject_skip', type=int, default=0, help='How many subjects to skip from beginning of list.')
parser.add_argument('--max-images', dest='max_images', type=int, default=-1, help='Maximum number of images per subject.')
parser.add_argument('--iterations', dest='iterations', type=int, default=1, help='Number of times to iterate over data.')
parser.add_argument('--enrol', dest='enrol', action='store_true', help='Enrol subjects instead of searching them.')
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Be more verbose.')
args = parser.parse_args()

importer = ImportImageDir()

if args.create_watchlists:
    importer.create_watchlists()
    exit(0)

if args.delete_subjects:
    importer.delete_all_subjects()
    exit(0)


subject_data = importer.get_subject_data(image_dir=args.image_dir,
                                         id_list=args.id_list,
                                         number_of_subjects=args.max_subjects,
                                         max_faces_per_subject=args.max_images,
                                         subject_skip=args.subject_skip)


results = Dict()
results.total_success = 0
results.total_failure = 0
results.total_time = 0

for i in range(0, args.iterations):
    tic = time.time()
    if args.enrol:
        (success, failure) = importer.enrol_data(subject_data)
    else:
        (success, failure) = importer.search_data(subject_data)

    toc = time.time()
    seconds = toc-tic
    results.total_success += success
    results.total_failure += failure
    results.total_time += seconds
    print("iteration, {}, success, {}, failure, {}, total_time, {}, images_per_second, {}".format(i, success, failure, seconds, (success+failure)/seconds))

avg_success = results.total_success/args.iterations
avg_failure = results.total_failure/args.iterations
avg_time = results.total_time/args.iterations
print("iteration, avg, success, {}, failure, {}, total_time, {}, images_per_second, {}".format(avg_success, avg_failure, avg_time, (avg_success+avg_failure)/avg_time))

