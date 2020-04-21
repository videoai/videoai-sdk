# Benchmark 
In this directory are some tools to help benchmark a server.

## Pre-requisites

* Access to a SmartVis Face Server
* Valid account on the SmartVis Face Server, i.e. username and password
* Developer keys.
* Lots of image data

## Developer Keys

In your home directory you need to create a file __.videoai__ which has the following format.

```bash
[videoai.net]
email=demo@digitalbarriers.com
password=XXXXXX
client_id =  YYYYYYYYY
client_secret =  ZZZZZZZZ
```

You will need to obtain the __client_id__ and __client_secret__ from Digital Barriers.

## Image Data

There is some example image data [here](data).  It is stored as

* John Smith
  * image1.jpg
  * image2.jpg
* Jane Doe
  * jane1.jpg
  * jane2.jpg
  
Note, the image file names are not important. 

## Quick Start

If you have an empty database you need to create some watchlists.

```shell script
python benchmark.py --authentication-server=http://192.168.86.197:10000 --workers 64 --create-watchlists
```

If you want to enrol lots of subjects.

```shell script
python benchmark.py --authentication-server=http://192.168.86.197:10000 --workers 64 --image-dir=data --enrol
```

If you want to perform lots of searches.
```shell script
python benchmark.py --authentication-server=http://192.168.86.197:10000 --workers 64 --image-dir=data
```

## Usage

```text
python benchmark.py --help
usage: benchmark.py [-h] [--image-dir IMAGE_DIR] [--id-list ID_LIST]
                    [--workers WORKERS] [--key-file KEY_FILE]
                    [--authentication-server AUTHENTICATION_SERVER]
                    [--create-watchlists] [--delete-subjects]
                    [--max-subjects MAX_SUBJECTS]
                    [--subject_skip SUBJECT_SKIP] [--max-images MAX_IMAGES]
                    [--iterations ITERATIONS] [--enrol] [--verbose]

Benchmark SmartVis Face Server

optional arguments:
  -h, --help            show this help message and exit
  --image-dir IMAGE_DIR
                        The image directory. (default: /mnt/image-
                        db/FaceDatabase/DATABASE/images)
  --id-list ID_LIST     Get ids from this file. (default: None)
  --workers WORKERS     The number of worker threads. (default: 64)
  --key-file KEY_FILE   The number of worker threads. (default:
                        /home/kieron/.videoai)
  --authentication-server AUTHENTICATION_SERVER
                        The authentication server to use. (default:
                        http://192.168.86.197:10000)
  --create-watchlists   Create the watchlists. (default: False)
  --delete-subjects     Delete all the subjects. (default: False)
  --max-subjects MAX_SUBJECTS
                        How many subjects to enrol. (default: -1)
  --subject_skip SUBJECT_SKIP
                        How many subjects to skip from beginning of list.
                        (default: 0)
  --max-images MAX_IMAGES
                        Maximum number of images per subject. (default: -1)
  --iterations ITERATIONS
                        Number of times to iterate over data. (default: 1)
  --enrol               Enrol subjects instead of searching them. (default:
                        False)
  --verbose             Be more verbose. (default: False)

Digital Barriers.
```

## Notes

* The number of workers are how many concurrent requests to the server are made.
* When benchmarking it is important to know that the bandwidth to the server is high-enough to cope with all the image data you are sending.



