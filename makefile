
IMAGE:=snapcast-zones-image
NAME:=snapcast-zones

build-image:
	docker build -t ${IMAGE} .

run-docker:
	docker run --rm -d -v ${PWD}/config.yml:/usr/src/app/config.yml --name ${NAME} ${IMAGE}

restart-docker:
	docker restart ${NAME}
stop-docker:
	docker stop ${NAME}
logs:
	docker logs -f ${NAME}
bash:
	docker exec -it ${NAME} bash
