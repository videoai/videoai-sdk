KEY_FILE ?= ~/.videoai
VERBOSE ?= --verbose
AUTHENTICATION_SERVER ?= http://192.168.86.197:8001

RECOGNITION = python recognition.py --key-file ${KEY_FILE} --authentication-server ${AUTHENTICATION_SERVER} ${VERBOSE}
AUTHENTICATE = python face_authenticate.py --key-file ${KEY_FILE} --authentication-server ${AUTHENTICATION_SERVER} ${VERBOSE}

enrol:
	${RECOGNITION} --image unittests/images/000_1_1.jpg --name John --create-subject
	${RECOGNITION} --image unittests/images/030_1_1.jpg --name Paul --create-subject

identify:
	${RECOGNITION} --image unittests/images/000_4_1.jpg --recognition
	${RECOGNITION} --image unittests/images/030_4_1.jpg --recognition

subjects:
	${RECOGNITION} --subjects

image-dir:
	${RECOGNITION} --image-dir unittests/images

delete:
	${RECOGNITION} --delete-subjects

authenticate_pass:
	${AUTHENTICATE} --gallery unittests/images/000_1_1.jpg --probe unittests/images/000_4_1.jpg

authenticate_fail:
	${AUTHENTICATE} --gallery unittests/images/000_1_1.jpg --probe unittests/images/030_1_1.jpg


