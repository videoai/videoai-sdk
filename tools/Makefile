
AUTHENTICATION_SERVER ?= http://192.168.86.222:8001
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

enrol-ids:
	${BENCHMARK} --image-dir /mnt/image-db/FaceDatabase/DATABASE/images --id-list /mnt/image-db/FaceDatabase/DATABASE/all_ids.list --max-subjects 100000 --max-images 5 --enrol

xm:
	${BENCHMARK} --image-dir /buf/image-db/thumbnails --enrol --iterations 100 

dev:
	${BENCHMARK} --image-dir /mnt/image-db/xm2vts/thumbnails --enrol --iterations 1

