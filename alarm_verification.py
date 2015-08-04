from videoai import AlarmVerification
import os

alarm_verification_data_dir = os.path.join('..','test-data','AlarmVerification')

alarm_verification = AlarmVerification()

video_file = os.path.join(alarm_verification_data_dir, 'officeEntry.mp4')
task = alarm_verification.apply(video_file)
print 'Video {}, probability of alarm {}%'.format(video_file, task['probability'])

# OK we can download the video which contains the OSD
alarm_verification.download_file(task['results_video'], 'somevideo.avi')
