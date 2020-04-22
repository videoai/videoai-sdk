
# VideoAI.net SDK

In this repository there is a Python SDK for calling the SmartVis Face API. 

## Pre-requisites

* Access to a SmartVis Face Server
* Valid account on the SmartVis Face Server, i.e. username and password
* Developer keys.

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

## Running the Examples

In the file [recognition.py](recognition.py) there are some examples on how to use the SDK.

### Enrol a Subject

```shell script
python recognition.py --authentication-server http://192.168.86.197:10000  --image unittests/images/000_1_1.jpg --name John --create-subject
```

### Perform Recognition

```shell script
python recognition.py --authentication-server http://192.168.86.197:10000  --image unittests/images/000_4_1.jpg --recognition
```

### Authenticate Two Images 

```shell script
python face_authenticate.py --authentication-server http://192.168.86.197:10000 --gallery unittests/images/000_1_1.jpg --probe unittests/images/000_4_1.jpg
```





