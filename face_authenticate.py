from videoai.recognition import Recognition
from videoai import FaceAuthenticate
import argparse, glob, os


parser = argparse.ArgumentParser(description='Authenticate images.', epilog='Have fun using authenticating.')
parser.add_argument('--key-file', dest='key_file', default=os.path.join(os.path.expanduser("~"), ".videoai"),  help='Path to your developer keys.')
parser.add_argument('--authentication-server', dest='authentication_server', default='http://192.168.86.197:10000', help='The authentication server to use.')
parser.add_argument('--gallery', dest='gallery', required=True, help='Gallery image')
parser.add_argument('--probe', dest='probe', required=True, help='Probe image')
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Be more verbose')
parser.add_argument('--download', dest='download', action='store_true', help='Download any results')
parser.set_defaults(download=False)
args = parser.parse_args()


# recognition on an image
print('Perform authentication between {} and {}'.format(args.gallery, args.probe))
face_authenticate = FaceAuthenticate.create(key_file=args.key_file,
                                            authentication_server=args.authentication_server,
                                            verbose=args.verbose)

results = face_authenticate.apply(gallery=args.gallery,
                                  probe1=args.probe,
                                  download=args.download)


if results['authenticated']:
    print('Identity Authenticated with score {0:2f}'.format(results['score']))
else:
    print('Identity NOT Authenticated')

