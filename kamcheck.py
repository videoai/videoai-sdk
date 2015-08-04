from videoai import KamCheck
import os

kamcheck_data_dir = os.path.join('..','test-data','KamCheck')
#kamcheck_data_dir = '/ebuf/kieron/src/papillon/src/Data/Samples'

kamcheck = KamCheck()

# Example of tampering
image_file = os.path.join(kamcheck_data_dir, 'PTZRef.png')
video_file = os.path.join(kamcheck_data_dir, 'PTZ.avi')
task = kamcheck.apply(image_file, video_file)
print 'Reference {0}, video {1}, probability of tampering {2}%'.format(image_file, video_file, task['probability'])

# Example of no tampering
image_file = os.path.join(kamcheck_data_dir, 'parkingRef.png')
video_file = os.path.join(kamcheck_data_dir, 'parking.avi')
task = kamcheck.apply(image_file, video_file)
print 'Reference {0}, video {1}, probability of tampering {2}%'.format(image_file, video_file, task['probability'])

