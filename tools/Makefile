
AUTHENTICATION_SERVER ?= http://192.168.86.222:10000
IMAGE_DIR ?= data
WORKERS ?= 64

BENCHMARK = python benchmark.py --authentication-server=${AUTHENTICATION_SERVER} --workers ${WORKERS}
DELL_BENCHMARK = python benchmark.py --authentication-server=http://192.168.86.222:10000 --workers ${WORKERS}

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

dell-enrol:
	${DELL_BENCHMARK} --image-dir /buf/image-db/thumbnails --enrol --iterations 106

dell-search:
	${DELL_BENCHMARK} --image-dir /buf/image-db/thumbnails --iterations 10

dell-verify-assure-enrol:
	${DELL_BENCHMARK} --image-dir /buf/image-db/thumbnails --verify-assure-enrol --max-subjects 295 --max-images 3 --iterations 50

dell-verify-assure:
	${DELL_BENCHMARK} --image-dir /buf/image-db/thumbnails --verify-assure --max-subjects 295 --max-images 8 --iterations 10

verify-assure-enrol:
	${BENCHMARK} --image-dir /mnt/image-db/xm2vts/thumbnails --verify-assure-enrol --max-subjects 295 --max-images 3 --iterations 530 

verify-assure:
	${BENCHMARK} --image-dir /mnt/image-db/xm2vts/thumbnails --verify-assure --skip-subjects 231 --max-subjects 64 --max-images 1 --iterations 2

enrol:
	${BENCHMARK} --image-dir /mnt/image-db/xm2vts/thumbnails --enrol --iterations 2

search:
	${BENCHMARK} --image-dir /mnt/image-db/xm2vts/thumbnails --iterations 1

