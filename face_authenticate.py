from videoai.recognition import Recognition
from videoai import FaceAuthenticate
import argparse, glob, os


parser = argparse.ArgumentParser(description='Authenticate images.', epilog='Have fun using authenticating.')
parser.add_argument('--gallery', dest='gallery', required=True, help='Gallery image')
parser.add_argument('--probe1', dest='probe1', required=True, help='First probe image')
parser.add_argument('--probe2', dest='probe2', help='Second probe image')
parser.add_argument('--key-file', dest='key_file', help='use this file for your keys (otherwise defaults ~/.video)')
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Be more verbose')
parser.add_argument('--download', dest='download', action='store_true', help='Download any results')
parser.set_defaults(download=False)
args = parser.parse_args()


# recognition on an image
print('Perform authentication on {}'.format(args.gallery))
face_authenticate = FaceAuthenticate.create(key_file=args.key_file, verbose=args.verbose)

results = face_authenticate.apply(gallery=args.gallery,
                                  probe1=args.probe1,
                                  probe2=args.probe2,
                                  download=args.download)

if results['authenticated']:
    print('Identity Authenticated with score {0:2f}'.format(results['score']))
else:
    print('Identity NOT Authenticated')

