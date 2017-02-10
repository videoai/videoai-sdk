from videoai import VideoAIUser, FaceLog, FaceLogImage
import argparse


# Sort out argument parsing
def zero_or_one(value):
    ivalue = int(value)
    if not (ivalue == 0 or ivalue == 1):
         raise argparse.ArgumentTypeError("%s is neither zero or one" % value)
    return ivalue


def min_size(value):
    ivalue = int(value)
    if ivalue < 20:
         raise argparse.ArgumentTypeError("%s is too small" % value)
    return ivalue


def between_zero_and_one(value):
    ivalue = float(value)
    if not (ivalue >=0 and ivalue <=1):
        raise argparse.ArgumentTypeError("%s needs to be between 0 and 1" % value)
    return ivalue

parser = argparse.ArgumentParser(description='VideoAI command line tool.', epilog='Have fun using VideoAI.')
parser.add_argument('-i', '--image', dest='image', help='specify an image')
parser.add_argument('-v', '--video', dest='video', help='specify a video to use')
parser.add_argument('--email', dest='email', help='The email address')
parser.add_argument('--pwd', dest='pwd', help='The password')
parser.add_argument('--auth', dest='auth', help='The authentication server')
parser.add_argument('--key-file', dest='key_file', help='use this file for your keys (otherwise defaults ~/.video)')
parser.add_argument('--face-log-image', dest='face_log_image', action='store_true', help='Perform FaceLog on '
                                                                                           'image')
parser.add_argument('--face-log', dest='face_log', action='store_true', help='Perform FaceLog on video')
parser.add_argument('--download', dest='download', action='store_true', help='Download any results')
parser.add_argument('--no-download', dest='download', action='store_false', help='Do not download any results')
parser.add_argument('--recognition', dest='recognition', action='store_true', help='If doing face-log, perform recognition from default watchlist')
parser.add_argument('--compare-threshold', type=between_zero_and_one, dest='compare_threshold', default=0.8, help='When doing face-recognition, apply this threshold (0 to 1)')
parser.add_argument('--start-frame', dest='start_frame', default=0, help='Start processing at this frame in the video')
parser.add_argument('--max-frames', dest='max_frames', default=0, help='Process this many frames (0 do all)')
parser.add_argument('--min-size', dest='min_size', type=min_size, default=30, help='If searching for objects (e.g. faces) then this is the minimum size')
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Be more verbose')
parser.add_argument('--tasks', dest='tasks', action='store_true', help='List all tasks')
parser.set_defaults(download=True)
args = parser.parse_args()

if args.face_log_image:
    print "performing face log on image"
    face_log_image = FaceLogImage.create(email=args.email,
                                         password=args.pwd,
                                         key_file=args.key_file,
                                         authentication_server=args.auth,
                                         verbose=args.verbose)
    if args.tasks:
        face_log_image.tasks()
    else:
        task = face_log_image.apply(image_file=args.image,
                                    download=args.download,
                                    recognition=args.recognition,
                                    compare_threshold=args.compare_threshold,
                                    min_size=args.min_size)

elif args.face_log:
    print "performing face log"
    face_log = FaceLog.create(email=args.email,
                              password=args.pwd,
                              key_file=args.key_file,
                              authentication_server=args.auth,
                              verbose=args.verbose)
    if args.tasks:
        face_log.tasks()
    else:
        task = face_log.apply(video_file=args.video,
                              download=args.download,
                              recognition=args.recognition,
                              compare_threshold=args.compare_threshold,
                              start_frame=args.start_frame,
                              max_frames=args.max_frames,
                              min_size=args.min_size)



else:
    print "listing tasks"
    videoai = VideoAIUser.create(email=args.email,
                                 password=args.pwd,
                                 key_file=args.key_file,
                                 authentication_server=args.auth,
                                 verbose=args.verbose)
    if args.tasks:
        videoai.tasks()
