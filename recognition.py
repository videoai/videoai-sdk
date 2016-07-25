from videoai.recognition import Recognition
from videoai import FaceLogImage
import argparse
import sys


parser = argparse.ArgumentParser(description='VideoAI command line tool.', epilog='Have fun using VideoAI.')
parser.add_argument('-i', '--image', dest='image', help='specify an image')
parser.add_argument('-v', '--video', dest='video', help='specify a video to use')
parser.add_argument('--host', dest='host', default='', help='The VideoAI host to use')
parser.add_argument('--key-file', dest='key_file', help='use this file for your keys (otherwise defaults ~/.video)')
parser.add_argument('--name', dest='name', help='The subject name.')
parser.add_argument('--create-subject', dest='create_subject', action='store_true', help='Create subject from image.')
parser.add_argument('--subjects', dest='subjects', action='store_true', help='List all subjects in database.')
parser.add_argument('--gender', dest='gender', default='Unknown', help='Gender of subject.')
parser.add_argument('--tags', dest='tags', action='store_true', help='List all the tags')
parser.add_argument('--tagged', dest='tagged', action='store_true', help='List all the tagged object')
parser.add_argument('--tag', dest='tag', default='Unknown', help='A tag name.')
parser.add_argument('--create', dest='create', action='store_true', help='Create a tag')
parser.add_argument('--colour', dest='colour', default='#95a5a6', help='Create a tag with this colour')
parser.add_argument('--delete', dest='delete', action='store_true', help='Delete a tag(s).')
parser.add_argument('--default', dest='default', action='store_true', help='Create a default set of tags for user')
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Be more verbose')
parser.add_argument('--delete-subjects', dest='delete_subjects', action='store_true', help='delete all subjects')
parser.set_defaults(download=True)
args = parser.parse_args()

recognition = Recognition(host=args.host, key_file=args.key_file, verbose=args.verbose)

# List subjects
if args.subjects:
    print "Listing all the subjects"
    tags = recognition.list_subjects()

if args.delete_subjects:
    print 'Deleting all the subjects in your database'
    subjects = recognition.list_subjects()
    for subject in subjects:
        subject_id = subject['subject_id']
        print ' - deleting subject {}'.format(subject_id)
        recognition.delete_subject(subject_id)

# Create a subject
if args.create_subject and not args.image:
    print 'Going to create a subject with name {}, with tag {} and gender {}'.format(args.name, args.tag, args.gender)

    # Lets create the subject
    user_data = {'gender': args.gender, 'notes': ''}
    subject = recognition.create_subject(name=args.name, tag=args.tag, user_data=user_data)
    subject_id = subject['subject_id']
    print 'Created subject with id {}'.format(subject_id)

# Create a subject from an image
if args.create_subject and args.image:
    print 'Going to create a subject with name {}, with tag {} and gender {}'.format(args.name, args.tag, args.gender)

    # Lets run a face-log on the image
    try:
        face_log_image = FaceLogImage(host=args.host, key_file=args.key_file, verbose=args.verbose)
        result = face_log_image.apply(image_file=args.image,
                                      download=False,
                                      min_size=80)
        if result['number_of_faces'] != 1:
            raise Exception('Not enough or too many faces have been found')

        # The face of interest is the first one
        face = result['detections'][0]

        # Lets create the subject
        user_data = {'gender': args.gender, 'notes': ''}
        subject = recognition.create_subject(name=args.name, tag=args.tag, user_data=user_data)
        subject_id = subject['subject_id']
        print 'Created subject with id {}'.format(subject_id)

        # Now lets join a subject to a detection
        recognition.add_detection_to_subject(face['detection_id'], subject_id)

    except:
        raise Exception('Failed to create a subject from an input image')


# List tags
if args.tags:
    print "Listing all the tags"
    tags = recognition.list_tags()

# List tags
if args.tagged:
    print "Listing all the tags"
    tags = recognition.list_tagged(args.tag, args.object)

# Generic delete tag
elif args.delete:
    try:
        recognition.delete_tag(tag_name=args.tag, object_id=args.object)
    except:
        print 'Unable to delete tag id'

# Generic update tags
elif args.create:
    try:
        recognition.create_tag(args.tag)
    except:
        print 'Failed to create tag {}'.format(args.tag)

# Generic update tags
elif args.default:
    try:
        recognition.default_tags()
    except:
        print 'Failed to create default tags'

