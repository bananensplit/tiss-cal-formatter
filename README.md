# TISS Calendar Formatter

## Development
### Backend
For the backend to work properly you need to setup a MongoDB database and a Redis database. It is recommended to do this with docker containers for easier handeling and configuration.

**On Linux**
```bash
# Pull containers
docker pull mongo
docker pull redis

# Setup MongoDB
docker run --name tisscal-mongo -d \
    -p 8881:27017 \
    -e MONGO_INITDB_ROOT_USERNAME=root \
	-e MONGO_INITDB_ROOT_PASSWORD=rootPassword \
    mongo

# Setup Redis
docker run --name tisscal-redis -d \
    -p 8882:27017 \
    redis

# Setup virtual environment
cd backend
python -m virutalenv venv
source ./venv/bin/activate
pip install -r requirements.txt

# Create .env file
echo BASE_URL="/" >> .env
echo MONGO_CONNECTION_STRING="mongodb://root:rootPassword@localhost:8881" >> .env
echo REDIS_HOST="localhost" >> .env
echo REDIS_PORT=8882 >> .env
echo REDIS_PASSWORD="None" >> .env
echo DEVELOPMENT_MODE=True >> .env

# Startup
uvicorn main:app --reload
```

**On Windows**
```powershell
# Pull containers
docker pull mongo
docker pull redis

# Setup MongoDB
docker run --name tisscal-mongo -d `
    -p 8881:27017 `
    -e MONGO_INITDB_ROOT_USERNAME=root `
	-e MONGO_INITDB_ROOT_PASSWORD=rootPassword `
    mongo

# Setup Redis
docker run --name tisscal-redis -d `
    -p 8882:6379 `
    redis

# Setup virtual environment
cd backend
python -m virtualenv venv
& ./venv/Scripts/activate
pip install -r requirements.txt

# Create .env file
echo BASE_URL="/" >> .env
echo MONGO_CONNECTION_STRING="mongodb://root:rootPassword@localhost:8881" >> .env
echo REDIS_HOST="localhost" >> .env
echo REDIS_PORT=8882 >> .env
echo REDIS_PASSWORD="None" >> .env
echo DEVELOPMENT_MODE=True >> .env

# Startup
uvicorn main:app --reload
```

**User**
```json
# This corresponds to a DB entry for the user 'test' with the password 'ganzGeheim123!' (without the _id key)
{
    "username": "test",
    "uernameLower": "test",
    "password": "57e1cb033bab879e5dbf2de52dda40faf9a4e3b68eca133a920d70751218d367"
}
```


### Frontend
To setup the frontend development you don't really need many things:

```powershell
cd frontend
npm install
npm run dev
# when you want it to be accaessible from other devices on under your IP
#npm run dev -- --host
```