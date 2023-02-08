# Tiss-Calendar Formatter - Backend

## Setup
```bash
# Setup redis
docker run --name tisscal-redis -p 8881:6379 -d redis

# Setup mongo
docker run --name tisscal-mongo -d \
    -p 8882:27017 \
    -e MONGO_INITDB_ROOT_USERNAME=admin \
	-e MONGO_INITDB_ROOT_PASSWORD=adminadmin \
    mongo
```


