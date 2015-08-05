from videoai import KamCheck, AlarmVerification, FaceDetect, FaceDetectImage, FaceLog
import argparse


# Sort out argument parsing
def zero_or_one(value):
    ivalue = int(value)
    if not (ivalue == 0 or ivalue == 1):
         raise argparse.ArgumentTypeError("%s is neither zero or one" % value)
    return ivalue


def min_size(value):
    ivalue = int(value)
    if ivalue < 30:
         raise argparse.ArgumentTypeError("%s is too small" % value)
    return ivalue


parser = argparse.ArgumentParser(description='VideoAI command line tool.', epilog='Have fun using VideoAI.')
parser.add_argument('-i', '--image', dest='image', help='specify an image')
parser.add_argument('-v', '--video', dest='video', help='specify a video to use')
parser.add_argument('--key-file', dest='key_file', help='use this file for your keys (otherwise defaults ~/.video)')
parser.add_argument('--kamcheck', dest='kamcheck', action='store_true', help='Perform kamcheck on image and video')
parser.add_argument('--alarm-verification', dest='alarm_verification', action='store_true', help='Perform alarm verification on video')
parser.add_argument('--face-detect', dest='face_detect', action='store_true', help='Perform FaceDetect on video')
parser.add_argument('--face-detect-image', dest='face_detect_image', action='store_true', help='Perform FaceDetect on image')
parser.add_argument('--face-log', dest='face_log', action='store_true', help='Perform FaceLog on video')
parser.add_argument('--download', dest='download', action='store_true', help='Download any results')
parser.add_argument('--no-download', dest='download', action='store_false', help='Do not download any results')
parser.add_argument('--blur', dest='blur', type=zero_or_one, default=0, help='If doing some face-detection, blur the faces in the output media')
parser.add_argument('--start-frame', dest='start_frame', default=0, help='Start processing at this frame in the video')
parser.add_argument('--max-frames', dest='max_frames', default=0, help='Process this many frames (0 do all)')
parser.add_argument('--min-size', dest='min_size', type=min_size, default=30, help='If searching for objects (e.g. faces) then this is the minimum size')
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Be more verbose')
parser.set_defaults(download=True)
args = parser.parse_args()

if args.kamcheck:
    print "performing kamcheck"
    kamcheck = KamCheck(verbose=args.verbose)
    task = kamcheck.apply(image_file=args.image, video_file=args.video)

if args.alarm_verification:
    print "performing alarm verification"
    alarm_verification = AlarmVerification(key_file=args.key_file, verbose=args.verbose)
    task = alarm_verification.apply(video_file=args.video, download=args.download)

if args.face_detect:
    print "performing face detection"
    face_detect = FaceDetect(verbose=args.verbose)
    task = face_detect.apply(video_file=args.video,
                             download=args.download,
                             blur=args.blur,
                             start_frame=args.start_frame,
                             max_frames=args.max_frames,
                             min_size=args.min_size)

if args.face_detect_image:
    print "performing face detection on image"
    face_detect_image = FaceDetectImage(verbose=args.verbose)
    task = face_detect_image.apply(image_file=args.image,
                                   download=args.download,
                                   blur=args.blur,
                                   min_size=args.min_size)

if args.face_log:
    print "performing face log"
    face_log = FaceLog(verbose=args.verbose)
    task = face_log.apply(video_file=args.video,
                          download=args.download,
                          blur=args.blur,
                          start_frame=args.start_frame,
                          max_frames=args.max_frames,
                          min_size=args.min_size)
