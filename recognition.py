from videoai.recognition import Recognition 
import argparse


parser = argparse.ArgumentParser(description='VideoAI command line tool.', epilog='Have fun using VideoAI.')
parser.add_argument('-i', '--image', dest='image', help='specify an image')
parser.add_argument('-v', '--video', dest='video', help='specify a video to use')
parser.add_argument('--host', dest='host', default='', help='The VideoAI host to use')
parser.add_argument('--key-file', dest='key_file', help='use this file for your keys (otherwise defaults ~/.video)')
parser.add_argument('--tags', dest='tags', action='store_true', help='List all the tags')
parser.add_argument('--tag', dest='tag', help='A tag name.')
parser.add_argument('--new-tag', dest='new_tag', help='Update this tag to new-tag.')
parser.add_argument('--delete', dest='delete', action='store_true', help='Delete a tag(s).')
parser.add_argument('--object', dest='object', help='Perform delete.')
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Be more verbose')
parser.set_defaults(download=True)
args = parser.parse_args()

recognition = Recognition(host=args.host, key_file=args.key_file, verbose=args.verbose)

# List tags
if args.tags:
    print "Listing all the tags"
    tags = recognition.list_tags(args.tag, args.object)


# Generic delete tag
elif args.delete:
    try:
        recognition.delete_tag(tag_name=args.tag, object_id=args.object)
    except:
        print 'Unable to delete tag id'

# Generic update tags
elif args.tag:
    try:
        recognition.tag_object(args.tag, args.object, args.new_tag)
    except:
        print 'Failed to create tag {}'.format(args.tag)


