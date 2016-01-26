from videoai import VideoAIUser
import argparse


parser = argparse.ArgumentParser(description='VideoAI command line tool.', epilog='Have fun using VideoAI.')
parser.add_argument('--host', dest='host', default='', help='The VideoAI host to use')
parser.add_argument('--key-file', dest='key_file', help='use this file for your keys (otherwise defaults ~/.video)')
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Be more verbose')
args = parser.parse_args()
    
# Check working OK
print "Listing tasks..."
videoai = VideoAIUser(host=args.host, key_file=args.key_file, verbose=args.verbose)
videoai.tasks()

# Print out some equivalent Curl commands, to use as a guide.

# List tasks
print "To list tasks in using Curl and your key..."
print "curl -L -H \"Authorization: {0}\" {1}/task".format(videoai.header['Authorization'], videoai.base_url)

# Detect face in image
print "To perform face detection on an image using your key using curl.."
print "curl -L -H \"Authorization: {0}\" -F image=@test_image.jpg {1}/face_detect".format(videoai.header['Authorization'], videoai.base_url)


# Detect face in video
print "To perform face detection on an image using your key using curl.."
print "curl -L -H \"Authorization: {0}\" -F video=@test_video.mp4 {1}/face_detect".format(videoai.header['Authorization'], videoai.base_url)






