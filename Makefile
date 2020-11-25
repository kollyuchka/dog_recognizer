start:
	docker-compose up -d

stop:
	docker-compose stop

down:
	docker-compose down

build:
	docker-compose build

restart: stop start

rebuild: down build start

rasa/init:
	docker-compose run rasa init --no-prompt --init-dir /app


rasa/train:
	docker-compose run rasa train



