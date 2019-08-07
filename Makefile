KEY_FILE ?= my.keys 
VERBOSE ?= --verbose

RECOGNITION = python recognition.py --key-file ${KEY_FILE} ${VERBOSE}

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
