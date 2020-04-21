
AUTHENTICATION_SERVER ?= http://192.168.86.197:8001
IMAGE_DIR ?= data
WORKERS ?= 64
BENCHMARK = python benchmark.py --authentication-server=${AUTHENTICATION_SERVER} --workers ${WORKERS}

init:
	${BENCHMARK} --create-watchlists

enrol:
	${BENCHMARK} --image-dir=${IMAGE_DIR} --enrol

search:
	${BENCHMARK} --image-dir=${IMAGE_DIR}

delete:
	${BENCHMARK} --delete-subjects
