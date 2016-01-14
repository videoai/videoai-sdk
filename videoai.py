from videoai import VideoAIUser, KamCheck, AlarmVerification, FaceDetect, FaceDetectImage, FaceLog, SafeZone2d
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


parser = argparse.ArgumentParser(description='VideoAI command line tool.', epilog='Have fun using VideoAI.')
parser.add_argument('-i', '--image', dest='image', help='specify an image')
parser.add_argument('-v', '--video', dest='video', help='specify a video to use')
parser.add_argument('--host', dest='host', default='', help='The VideoAI host to use')
parser.add_argument('--key-file', dest='key_file', help='use this file for your keys (otherwise defaults ~/.video)')
parser.add_argument('--kamcheck', dest='kamcheck', action='store_true', help='Perform kamcheck on image and video')
parser.add_argument('--kamcheck-reference', dest='kamcheck_reference', action='store_true', help='Select reference image from video')
parser.add_argument('--alarm-verification', dest='alarm_verification', action='store_true', help='Perform alarm verification on video')
parser.add_argument('--face-detect', dest='face_detect', action='store_true', help='Perform FaceDetect on video')
parser.add_argument('--face-detect-image', dest='face_detect_image', action='store_true', help='Perform FaceDetect on image')
parser.add_argument('--face-log', dest='face_log', action='store_true', help='Perform FaceLog on video')
parser.add_argument('--safezone-2d', dest='safezone_2d', action='store_true', help='Perform SafeZone.2d on video')
parser.add_argument('--download', dest='download', action='store_true', help='Download any results')
parser.add_argument('--no-download', dest='download', action='store_false', help='Do not download any results')
parser.add_argument('--blur', dest='blur', type=zero_or_one, default=0, help='If doing some face-detection, blur the faces in the output media')
parser.add_argument('--gender', dest='gender', action='store_true', help='If doing face-log, detect the gender of the faces')
parser.add_argument('--recognition', dest='recognition', action='store_true', help='If doing face-log, perform recognition from default watchlist')
parser.add_argument('--start-frame', dest='start_frame', default=0, help='Start processing at this frame in the video')
parser.add_argument('--min-certainty', dest='min_certainty', default=1.0, help='Minimum certainty to keep when doing face-log')
parser.add_argument('--max-frames', dest='max_frames', default=0, help='Process this many frames (0 do all)')
parser.add_argument('--min-size', dest='min_size', type=min_size, default=30, help='If searching for objects (e.g. faces) then this is the minimum size')
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Be more verbose')
parser.add_argument('--tasks', dest='tasks', action='store_true', help='List all tasks')
parser.set_defaults(download=True)
args = parser.parse_args()

if args.kamcheck:
    print "performing kamcheck"
    kamcheck = KamCheck(host=args.host, key_file=args.key_file, verbose=args.verbose)
    if args.tasks:
        kamcheck.tasks()
    else:
        task = kamcheck.apply(image_file=args.image, video_file=args.video)

elif args.kamcheck_reference:
    print "performing kamcheck get reference image"
    kamcheck = KamCheck(host=args.host, key_file=args.key_file, verbose=args.verbose)
    if args.tasks:
        kamcheck.tasks()
    else:
        task = kamcheck.get_reference_image(video_file=args.video)

elif args.alarm_verification:
    print "performing alarm verification"
    alarm_verification = AlarmVerification(host=args.host, key_file=args.key_file, verbose=args.verbose)
    if args.tasks:
        alarm_verification.tasks()
    else:
        tasks = alarm_verification.apply(video_file=args.video, download=args.download)

elif args.face_detect:
    print "performing face detection"
    face_detect = FaceDetect(host=args.host, key_file=args.key_file, verbose=args.verbose)
    if args.tasks:
        face_detect.tasks()
    else:
        task = face_detect.apply(video_file=args.video,
                                 download=args.download,
                                 blur=args.blur,
                                 start_frame=args.start_frame,
                                 max_frames=args.max_frames,
                                 min_size=args.min_size)

elif args.face_detect_image:
    print "performing face detection on image"
    face_detect_image = FaceDetectImage(host=args.host, key_file=args.key_file, verbose=args.verbose)
    if args.tasks:
        face_detect_image.tasks()
    else:
        task = face_detect_image.apply(image_file=args.image,
                                       download=args.download,
                                       blur=args.blur,
                                       min_size=args.min_size)

elif args.face_log:
    print "performing face log"
    face_log = FaceLog(host=args.host, key_file=args.key_file, verbose=args.verbose)
    if args.tasks:
        face_log.tasks()
    else:
        task = face_log.apply(video_file=args.video,
                              download=args.download,
                              gender=args.gender,
                              recognition=args.recognition,
                              start_frame=args.start_frame,
                              max_frames=args.max_frames,
                              min_size=args.min_size,
                              min_certainty=args.min_certainty)

elif args.safezone_2d:
    print "performing safezone_2d"
    safezone_2d = SafeZone2d(host=args.host, key_file=args.key_file, verbose=args.verbose)
    if args.tasks:
        safezone_2d.tasks()
    else:
        task = safezone_2d.apply(video_file=args.video,
                                 start_frame=args.start_frame,
                                 max_frames=args.max_frames,
                                 download=args.download)


else :
    print "listing tasks"
    videoai = VideoAIUser(host=args.host, key_file=args.key_file, verbose=args.verbose)
    if args.tasks:
        videoai.tasks()
