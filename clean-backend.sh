#!/usr/bin/env zsh

sudo docker kill tisscal-mongo
sudo docker kill tisscal-redis

sudo docker rm tisscal-mongo
sudo docker rm tisscal-redis
