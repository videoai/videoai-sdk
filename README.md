
# VideoAI.net SDK

In this repository there is an SDK for calling the VideoAI video analyics API.  So far just written in Python. 

To see a demo-portal for VideoAI, built using this SDK and the VideoAI API, point your browser to https://demo.videoai.net.

Documentation on the actual VideoAI REST API can be found at https://videoai.net/api.

## SDK Authentication

To use VideoAI you will need a pair of developer keys.  You can request these through the demo web-site.

To run any of the examples or unit tests you will need to put your supplied keys in your home directory in a file called .videoai in the following format.

```
[videoai.net]
apiKey_id = XXXXXXXXXXXXXXXXXXXXXX
apiKey_secret = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

The main Python videoai class will then pick them up and use them to authenticate against the VideoAI service.

## Basic HTTP Authentication

To generate a token from your key-pair to put into the Authorization field of the HTTP header, or to use on with a tool like curl.

```
import base64
api_key = "{0}:{1}".format(apiKey_id, apiKey_secret)
basic_auth_header = "Basic {0}".format(base64.b64encode(api_key))
```


## The Command Line Tool

There is a simple command line tool you can use to test most of VideoAI's current functionality.

The tool has a dependency on configparser: you can install this with "pip install configparser".

```
python videoai.py --help

usage: videoai.py [-h] [-i IMAGE] [-v VIDEO] [--key-file KEY_FILE]
                  [--kamcheck] [--alarm-verification] [--face-detect]
                  [--face-detect-image] [--face-log] [--download]
                  [--no-download] [--blur BLUR] [--start-frame START_FRAME]
                  [--max-frames MAX_FRAMES] [--min-size MIN_SIZE] [--verbose]

VideoAI command line tool.

optional arguments:
  -h, --help            show this help message and exit
  -i IMAGE, --image IMAGE
                        specify an image
  -v VIDEO, --video VIDEO
                        specify a video to use
  --key-file KEY_FILE   use this file for your keys (otherwise defaults
                        ~/.video)
  --kamcheck            Perform kamcheck on image and video
  --alarm-verification  Perform alarm verification on video
  --face-detect         Perform FaceDetect on video
  --face-detect-image   Perform FaceDetect on image
  --face-log            Perform FaceLog on video
  --download            Download any results
  --no-download         Do not download any results
  --blur BLUR           If doing some face-detection, blur the faces in the
                        output media
  --start-frame START_FRAME
                        Start processing at this frame in the video
  --max-frames MAX_FRAMES
                        Process this many frames (0 do all)
  --min-size MIN_SIZE   If searching for objects (e.g. faces) then this is the
                        minimum size
  --verbose             Be more verbose

Have fun using VideoAI.
```
### An Example

For example, to run FaceLog on the first 50 frames of a video.

```
python videoai.py --video ../test-data/FaceDetector/officeEntry.mp4 --face-log --max-frames 50
```
The following script would also download the video file with the OSD, an XML file detailing the location of the faces, the tracks and the sightings and a thumbnail for each unique sighting.

## Unit Tests

Included in this code are a set of unit tests which cover all the functionality of VideoAI.  Some more details about each unit test are given below.

To run any of the unit tests you will need to download the data from our test-data repository https://github.com/videoai/test-data

```
git clone https://github.com/videoai/test-data.git test-data
```

It is important that this data should reside in a test-data folder at the same level in as video-sdk directory.

### Face Detection on an Image

This runs a set of face-detection unit tests on an some images.

```
python unittests.py TestFaceDetectImage
```

As an example output you would expect to see.

```
Testing face detection...
** Testing KaliningradFaces.jpg with expected result 43 **
Requested FaceDetectImage on ../test-data/FaceDetector/KaliningradFaces.jpg (0.935788 Mb)
{
  "status": "success", 
  "task": {
    "analytic": "face_detect_image", 
    "complete": true, 
    "finish_time": "Mon, 17 Aug 2015 19:47:56 GMT", 
    "job_id": "5safUMyuDz7dh8VTKcrwbX", 
    "message": "Face detector found 43 faces", 
    "number_of_faces": 43, 
    "results_image": "http://54.195.251.39:5000/results/229/5safUMyuDz7dh8VTKcrwbX/face_detect_5safUMyuDz7dh8VTKcrwbX.jpg", 
    "results_xml": "http://54.195.251.39:5000/results/229/5safUMyuDz7dh8VTKcrwbX/face_detect_5safUMyuDz7dh8VTKcrwbX.xml", 
    "start_time": "Mon, 17 Aug 2015 19:47:56 GMT", 
    "success": true
  }
}
Downloading http://54.195.251.39:5000/results/229/5safUMyuDz7dh8VTKcrwbX/face_detect_5safUMyuDz7dh8VTKcrwbX.jpg to face_detect_5safUMyuDz7dh8VTKcrwbX.jpg
Downloading http://54.195.251.39:5000/results/229/5safUMyuDz7dh8VTKcrwbX/face_detect_5safUMyuDz7dh8VTKcrwbX.xml to face_detect_5safUMyuDz7dh8VTKcrwbX.xml

```

### Face Detection on Video

```
python unittests.py TestFaceDetect
```
Example output

```
Testing face detection...
** Video File officeEntry.mp4 w **
Requested FaceDetect on video ../test-data/FaceDetector/officeEntry.mp4 (0.342982 Mb)
{u'analytic': u'face_detect', u'message': u'In progess.', u'start_time': u'Mon, 17 Aug 2015 20:07:12 GMT', u'complete': False, u'job_id': u'4qA8FaSRs34b9MU5wD2MP3'}
{u'analytic': u'face_detect', u'message': u'In progess.', u'start_time': u'Mon, 17 Aug 2015 20:07:12 GMT', u'complete': False, u'job_id': u'4qA8FaSRs34b9MU5wD2MP3'}
{u'start_frame': 0, u'job_id': u'4qA8FaSRs34b9MU5wD2MP3', u'success': True, u'number_of_faces': 4, u'finish_time': u'Mon, 17 Aug 2015 20:07:28 GMT', u'start_time': u'Mon, 17 Aug 2015 20:07:12 GMT', u'results_video': u'http://54.195.251.39:5000/results/229/4qA8FaSRs34b9MU5wD2MP3/face_detect_4qA8FaSRs34b9MU5wD2MP3.m4v', u'analytic': u'face_detect', u'results_xml': u'http://54.195.251.39:5000/results/229/4qA8FaSRs34b9MU5wD2MP3/face_detect_4qA8FaSRs34b9MU5wD2MP3.xml', u'frames': -1, u'message': u'Face detector found 4 faces', u'frames_processed': 81, u'complete': True}
Downloading http://54.195.251.39:5000/results/229/4qA8FaSRs34b9MU5wD2MP3/face_detect_4qA8FaSRs34b9MU5wD2MP3.m4v to face_detect_4qA8FaSRs34b9MU5wD2MP3.m4v
Downloading http://54.195.251.39:5000/results/229/4qA8FaSRs34b9MU5wD2MP3/face_detect_4qA8FaSRs34b9MU5wD2MP3.xml to face_detect_4qA8FaSRs34b9MU5wD2MP3.xml

```

### Face Log

```
python unittests.py TestFaceLog
```
You would expect to see

```
Testing face detection...
** Testing officeEntry.mp4 **
Requested FaceLog on video ../test-data/FaceDetector/officeEntry.mp4 (0.342982 Mb)
{u'analytic': u'face_log', u'message': u'In progess.', u'start_time': u'Mon, 17 Aug 2015 20:16:40 GMT', u'complete': False, u'job_id': u'a5GZcVVJ8hR9Coh6A4XV4b'}
{u'analytic': u'face_log', u'message': u'In progess.', u'start_time': u'Mon, 17 Aug 2015 20:16:40 GMT', u'complete': False, u'job_id': u'a5GZcVVJ8hR9Coh6A4XV4b'}
{u'start_frame': 0, u'number_of_sightings': 1, u'complete': True, u'success': True, u'results_video': u'http://54.195.251.39:5000/results/229/a5GZcVVJ8hR9Coh6A4XV4b/face_log_a5GZcVVJ8hR9Coh6A4XV4b.m4v', u'finish_time': u'Mon, 17 Aug 2015 20:16:59 GMT', u'start_time': u'Mon, 17 Aug 2015 20:16:40 GMT', u'input_video': u'officeEntry.mp4', u'job_id': u'a5GZcVVJ8hR9Coh6A4XV4b', u'sightings': [{u'confidence': 0.133412718772888, u'start_frame': 32, u'end_frame': 35, u'frames': 4, u'sighting_id': u'e0b9ef8e-3b2d-4ec2-901e-9f39770233b0', u'thumbnail': u'http://54.195.251.39:5000/results/229/a5GZcVVJ8hR9Coh6A4XV4b/thumbnail_39f22934-728a-4ab8-8dfd-3680319effe0.jpg'}], u'analytic': u'face_log', u'results_xml': u'http://54.195.251.39:5000/results/229/a5GZcVVJ8hR9Coh6A4XV4b/face_log_a5GZcVVJ8hR9Coh6A4XV4b.xml', u'frames': -1, u'message': u'Face log found 1 sightings, 1 tracks and 4 faces ', u'resolution': u'600x800@-1.0fps', u'frames_processed': 81}
Downloading http://54.195.251.39:5000/results/229/a5GZcVVJ8hR9Coh6A4XV4b/face_log_a5GZcVVJ8hR9Coh6A4XV4b.m4v to face_log_a5GZcVVJ8hR9Coh6A4XV4b.m4v
Downloading http://54.195.251.39:5000/results/229/a5GZcVVJ8hR9Coh6A4XV4b/face_log_a5GZcVVJ8hR9Coh6A4XV4b.xml to face_log_a5GZcVVJ8hR9Coh6A4XV4b.xml
Downloading http://54.195.251.39:5000/results/229/a5GZcVVJ8hR9Coh6A4XV4b/thumbnail_39f22934-728a-4ab8-8dfd-3680319effe0.jpg to thumbnail_39f22934-728a-4ab8-8dfd-3680319effe0.jpg

```

### KamCheck

```
python unittests.py TestKamCheck
```

### Alarm Verification

```
python unittests.py TestAlarmVerification
```






