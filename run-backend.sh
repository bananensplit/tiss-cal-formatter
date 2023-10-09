#!/usr/bin/env zsh
cd ./backend
sudo python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt

rm .env
echo BASE_URL="/" >> .env
echo MONGO_CONNECTION_STRING="mongodb://root:rootPassword@localhost:8881" >> .env
echo REDIS_HOST="localhost" >> .env
echo REDIS_PORT=8882 >> .env
echo REDIS_PASSWORD="None" >> .env
echo DEVELOPMENT_MODE="True" >> .env

sudo docker run --name tisscal-mongo -d \
	-p 8881:27017 \
	-e MONGO_INITDB_ROOT_USERNAME=root \
	-e MONGO_INITDB_ROOT_PASSWORD=rootPassword \
	mongo

sudo docker run --name tisscal-redis -d \
	-p 8882:6379 \
	redis

uvicorn main:app --reload

