from videoai.recognition import Recognition
from videoai import FaceLogImage, FaceLog
import argparse, glob, os


parser = argparse.ArgumentParser(description='VideoAI command line tool.', epilog='Have fun using VideoAI.')
parser.add_argument('--image', dest='image', help='specify an image')
parser.add_argument('--image-dir', dest='image_dir', help='Enroll all images in this directory')
parser.add_argument('--video', dest='video', help='specify a video to use')
parser.add_argument('--recognition', dest='recognition', action='store_true', help='List all the tags')
parser.add_argument('--host', dest='host', default='', help='The VideoAI host to use')
parser.add_argument('--key-file', dest='key_file', help='use this file for your keys (otherwise defaults ~/.video)')
parser.add_argument('--name', dest='name', help='The subject name.')
parser.add_argument('--create-subject', dest='create_subject', action='store_true', help='Create subject from image.')
parser.add_argument('--delete-subjects', dest='delete_subjects', action='store_true', help='delete all subjects')
parser.add_argument('--delete-subject', dest='delete_subject', help='delete a subject with this id')
parser.add_argument('--subjects', dest='subjects', action='store_true', help='List all subjects in database.')
parser.add_argument('--gender', dest='gender', default='Unknown', help='Gender of subject.')
parser.add_argument('--tag', dest='tag', default='Unknown', help='A tag name to give a subject.')
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Be more verbose')
parser.add_argument('--download', dest='download', action='store_true', help='Download any results')
parser.set_defaults(download=False)
args = parser.parse_args()

recognition = Recognition(host=args.host, key_file=args.key_file, verbose=args.verbose)

# recognition on an image
if args.recognition and args.image:
    print 'Perform recognition on {}'.format(args.image)
    face_log_image = FaceLogImage(host=args.host, key_file=args.key_file, verbose=args.verbose)
    results = face_log_image.apply( image_file=args.image,
                                    download=args.download,
                                    recognition=True,
                                    min_size=80)
    print results

# recognition on a video
if args.recognition and args.video:
    print 'Perform recognition on {}'.format(args.video)
    face_log = FaceLog(host=args.host, key_file=args.key_file, verbose=args.verbose)
    results = face_log.apply( video_file=args.video,
                                    download=args.download,
                                    recognition=True,
                                    min_size=80)
    print results

# List all subjects
if args.subjects:
    print "Listing all the subjects"
    tags = recognition.list_subjects()

# Delete all subjects
if args.delete_subjects:
    print 'Deleting all the subjects in your database'
    try:
        subjects = recognition.list_subjects()
        for subject in subjects:
            subject_id = subject['subject_id']
            print ' - deleting subject {}'.format(subject_id)
            recognition.delete_subject(subject_id)
    except Exception as err:
        print('Trouble deleting subjects', err)

# Create a subject
if args.create_subject and not args.image:
    print 'Going to create a subject with name {}, with tag {} and gender {}'.format(args.name, args.tag, args.gender)

    try:
        # Lets create the subject
        user_data = {'gender': args.gender, 'notes': ''}
        subject = recognition.create_subject(name=args.name, tag=args.tag, user_data=user_data)
        subject_id = subject['subject_id']
        print 'Created subject with id {}'.format(subject_id)
    except Exception as err:
        print('Trouble creating subject', err)

# Create a subject from an enrollment image
def enrol_from_image(host, key_file, verbose, image, name, tag):
    try:
        face_log_image = FaceLogImage(host=host, key_file=key_file, verbose=verbose)
        result = face_log_image.apply(image_file=image,
                                      download=False,
                                      min_size=80)

        if result['number_of_faces'] != 1:
            raise Exception('Wrong amount of faces in input image')

        # The face of interest is the first one
        face = result['detections'][0]
        gender = face['gender']
        print face

        # Lets create the subject
        user_data = {'gender': gender, 'notes': ''}
        subject = recognition.create_subject(name=name, tag=tag, user_data=user_data)
        subject_id = subject['subject_id']
        print 'Created subject with id {}'.format(subject_id)

        # Now lets join a subject to a detection
        recognition.add_detection_to_subject(face['detection_id'], subject_id)
    except Exception as err:
        raise Exception(err)

if args.create_subject and args.image:
    print 'Going to create a subject with name {}, with tag {} and gender {}'.format(args.name, args.tag, args.gender)

    # Lets run a face-log on the image
    try:
        enrol_from_image(args.host, args.key_file, args.verbose, args.image, args.name, args.tag)
    except Exception as err:
        print('Trouble creating subject with image', err)

if args.image_dir:
    print 'Enrolling images in directory {}'.format(args.image_dir)

    image_files = glob.glob("{}/*".format(args.image_dir))
    valid_images = ['.jpg', '.gif', '.png']
    for image_file in image_files:

        basename = os.path.basename(image_file)
        name = os.path.splitext(basename)[0]
        ext = os.path.splitext(basename)[1].lower()
        if ext not in valid_images:
            continue
        try:
            print 'Enrolling {} from image {}'.format(name, image_file)
            enrol_from_image(args.host, args.key_file, args.verbose, image_file, name, args.tag)
        except:
            pass

# Delete a subject
if args.delete_subject:
    print 'Deleting subject with id {}'.format(args.delete_subject)
    try:
        recognition.delete_subject(args.delete_subject)
    except Exception as err:
        print('Trouble deleting subject', err)



