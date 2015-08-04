from videoai import FaceDetect
import os

alarm_verification_data_dir = os.path.join('..','test-data','AlarmVerification')

face_detect = FaceDetect()

video_file = os.path.join(alarm_verification_data_dir, 'officeEntry.mp4')
task = face_detect.apply(video_file)
print task
print 'Video {}'.format(video_file)

# OK we can download the video which contains the OSD
face_detect.download_file(task['results_video'])
