
# VideoAI.net SDK

To see a demo-portal for VideoAI, built using this SDK and the VideoAI API, point your browser to https://demo.videoai.net.

In this repository there is an SDK for calling the VideoAI API.  So far just written in Python.  

## Authentication

To use VideoAI you will need a pair of developer keys.  You can request these through the demo web-site.

To run any of the examples or unit tests you will need to put your supplied keys in your home directory in a file called .videoai in the following format.

```
[videoai.net]
apiKey_id = XXXXXXXXXXXXXXXXXXXXXX
apiKey_secret = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

The main Python videoai class will then pick them up and use them to authenticate against the VideoAI service.

## The Command Line Tool

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

## Running the Unit Tests

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

### Face Log

```
python unittests.py TestFaceLog
```

### KamCheck

```
python unittests.py TestKamCheck
```

### Alarm Verification

```
python unittests.py TestAlarmVerification
```






