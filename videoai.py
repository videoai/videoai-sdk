from videoai import KamCheck, AlarmVerification, FaceDetect
import argparse

parser = argparse.ArgumentParser(description='VideoAI command line tool.', epilog='Have fun using VideoAI.')

parser.add_argument('-i', '--image', dest='image', help='specify an image')
parser.add_argument('-v', '--video', dest='video', help='specify a video to use')
parser.add_argument('--kamcheck', dest='kamcheck', action='store_true', help='Perform kamcheck on image and video')
parser.set_defaults(kamcheck=False)
parser.add_argument('--alarm-verification', dest='alarm_verification', action='store_true', help='Perform alarm verification on video')
parser.set_defaults(alarm_verification=False)
parser.add_argument('--face-detect', dest='face_detect', action='store_true', help='Perform FaceDetect on video')
parser.set_defaults(face_detect=False)
parser.add_argument('--download', dest='download', action='store_true', help='Download any results.')
parser.add_argument('--no-download', dest='download', action='store_false', help='Do not download any results.')
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Be more verbose.')
parser.set_defaults(download=True)

args = parser.parse_args()

if args.kamcheck:
    print "performing kamcheck"
    kamcheck = KamCheck(verbose=args.verbose)
    task = kamcheck.apply(image_file=args.image, video_file=args.video)

if args.alarm_verification:
    print "performing alarm verification"
    alarm_verification = AlarmVerification(verbose=args.verbose)
    task = alarm_verification.apply(video_file=args.video, download=args.download)

if args.face_detect:
    print "performing face detection"
    face_detect = FaceDetect(verbose=args.verbose)
    task = face_detect.apply(video_file=args.video, download=args.download)
