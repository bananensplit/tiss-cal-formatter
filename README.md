# Tiss-Calendar-Formatter

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]




## A formatter for the [TISS](https://tiss.tuwien.ac.at) calendar for all **TU Wien students**

The [TISS](https://tiss.tuwien.ac.at) calendar provides a possibilty to download the events in the calendar as a `.ics` file. However the descriptions, locations and summary in this calendar are very short and particularly useful.
This is where the **Tiss-Calendar-Formatter** comes in. It provides you with a webinterface where you can edit the descriptions, locations and summary of the events in the calendar. After you are done editing the calendar, you can download the calendar as a `.ics` or import it to [a calendar application of your choice as an ical feed][import-ical-url].

This project is hosted at https://bananensplit.com/tisscal

You can...
* ... set templates for the **summary** of the events
* ... set templates for the **location** of the events
* ... set templates for the **description** of the events
* ... **remove** events from the calendar



Converts this event:       |  Into this event:
:-------------------------:|:-------------------------:
![][old-event-img]         |  ![][new-event-img]





## How to use?
> As of now the website is not mobile-optimized. I recommend using it on a laptop or pc.

### Create an account
1. Go to https://bananensplit.com/tisscal/register
2. Choose a username
3. Choose a password and retype the password. Please don't forget it, There is currently no way of resetting or changing your password.
4. Click on `Register`
5. When all went right, you should now be redirected to https://bananensplit.com/tisscal/calendars

### Create your calendar
1. Click on the '+' in the bottom right corner of the screen.
2. Enter a name for the calendar. This name is only for your convenience, so you can type whatever you want as long as you consider it useful.
3. Enter the Link
	1. Go to https://tiss.tuwien.ac.at/events/personSchedule.xhtml
	2. Scroll down. There should be a link that looks something like `https://tiss.tuwien.ac.at/events/rest/calendar/personal?locale=de&token=....`
	3. Copy this link and enter it in the textfield
4. Press `Submit`
5. If all went ok, you should be now able to see a box with two links and the name you typed.

### Get the formatted calendar
1. The formatted calendar is now provided to you via the second link as an `.ics` file (`https://bananensplit.com/tisscal/api/cal/***************************`)
2. Copy this link and paste it into your browser's searchbar to download the file or import it as an [iCal feed to the calendar of your choice](https://help.hospitable.com/en/articles/4605516-how-can-i-add-the-ical-feed-to-the-calendar-on-my-device)




## Installation

> **Note:** You need to have [Docker](https://www.docker.com/) installed on your machine. For windows you can use [Docker Desktop](https://www.docker.com/products/docker-desktop).


### Using `docker compose` (recommended)
Using **docker compose** you can simply run the following commands to start the whole project:

```powershell
# Clone this repository
git clone https://github.com/bananensplit/tiss-cal-formatter.git

# Go into the repository
cd tiss-cal-formatter

# Start the project
docker-compose up -d
```

This will start the whole project with the default parameters:
The webinterface will be available under `http://localhost:8111` and the API under `http://localhost:8111/api`.
If you want to change the default parameters, go to the [Advanced installation](#advanced-installation) section.




## Advanced installation

This are instructions for people who want to change the default parameters of the installation.
This section is designated for people who know what they are doing and have at least a base knowledge of `docker` and `docker compose` and are familiar with how it works.
If you are not familiar with `docker` and `docker compose`, i would recommend to go to [installation](#installation).


### Using `docker compose` with custom parameters

By default the webinterface will be available under `http://localhost:8111` and the API under `http://localhost:8111/api`.
If you want to change this behaviour the following information is for you.

If you want to change this default parameters, you can do so by editing the `docker-compose.yml` file.
* `BASE_URL`: is the base url of the webinterface. If you want to access the webinterface and the api under `http://localhost:8111/tisscal`, you have to set `BASE_URL` to `/tisscal`.
* `MONGO_CONNECTION_STRING`: is the connection string to the MongoDB database. Usefull when you want to use a remote database.
* `REDIS_HOST`: is the host of the Redis database. Usefull when you want to use a remote database.
* `REDIS_PORT`: is the port of the Redis database.
* `REDIS_PASSWORD`: is the password of the Redis database. Defaults to `None` (`""`).
* If you want to change the **port** of the webinterface, you have to change the port in the `ports` section of the `api` service. The default port is `8111`. Change it to `80` if you want to access the webinterface under `http://localhost`.
  
  ```yaml
  ...
    api:
        ...
        ports:
        - "8111:80" # -> "80:80"
  ...
  ```

When you are done editing the `docker-compose.yml` file, you can start the project with the following command:
```powershell
# Clone this repository
git clone https://github.com/bananensplit/tiss-cal-formatter.git

# Go into the repository
cd tiss-cal-formatter

# Start the project
docker-compose up -d
```


### Manually installing the project

If you want to install the formatter **manually**, you can follow the following steps and adjust the parameters to your needs:
```powershell
# Clone this repository
git clone https://github.com/bananensplit/tiss-cal-formatter.git

# Go into the repository
cd tiss-cal-formatter

# Pull necessary containers
docker pull mongo
docker pull redis
docker pull nikolaik/python-nodejs:python3.10-nodejs19

# Build the Docker container
docker build -t tiss-cal-formatter:1.0.0 \
    --build-arg BASE_URL="/" \
    .

# Setup MongoDB
docker run --name tisscal-mongo -d \
    -p 8881:27017 `
    -e MONGO_INITDB_ROOT_USERNAME=root \
    -e MONGO_INITDB_ROOT_PASSWORD=rootPassword \
    mongo

# Setup Redis
docker run --name tisscal-redis -d \
    -p 8882:6379 \
    redis

# Start the project
docker run -d \
    -p 80:80 \
    -e MONGO_CONNECTION_STRING="mongodb://root:rootPassword@localhost:8881" \
    -e REDIS_HOST="localhost" \
    -e REDIS_PORT=8882 \
    -e REDIS_PASSWORD="None" \
    tiss-cal-formatter:1.0.0
```




## How to setup for development

This are instructions for people who might want to contribute to this project.


### Prequisites
You need to have the following tools installed on your machine:
- [Docker](https://www.docker.com/)
- [Python 3.10](https://www.python.org/downloads/)
    - [virtualenv](https://pypi.org/project/virtualenv/)
- [Node.js 19](https://nodejs.org/en/download/) with npm


### Backend
```bash
# Clone this repository
git clone https://github.com/bananensplit/tiss-cal-formatter.git
cd tiss-cal-formatter/backend

# Setup virtual environment
python -m virutalenv venv
source ./venv/bin/activate   # on Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo BASE_URL="/" >> .env
echo MONGO_CONNECTION_STRING="mongodb://root:rootPassword@localhost:8881" >> .env
echo REDIS_HOST="localhost" >> .env
echo REDIS_PORT=8882 >> .env
echo REDIS_PASSWORD="None" >> .env
echo DEVELOPMENT_MODE="True" >> .env

# Pull containers
docker pull mongo
docker pull redis

# Setup MongoDB (hosts on port 8881)
docker run --name tisscal-mongo -d \
    -p 8881:27017 \
    -e MONGO_INITDB_ROOT_USERNAME=root \
    -e MONGO_INITDB_ROOT_PASSWORD=rootPassword \
    mongo

# Setup Redis (hosts on port 8882)
docker run --name tisscal-redis -d \
    -p 8882:6379 \
    redis

# Start the backend
uvicorn main:app --reload
```
The backend will be available under `http://localhost:8000/api`.


### Frontend
```bash
# Clone this repository
git clone https://github.com/bananensplit/tiss-cal-formatter.git
cd tiss-cal-formatter/frontend
npm install
npm run dev
```
The frontend will be available under `http://localhost:5173`.
When the frontend development server is running, it is configured to redirect all traffic going to `/api` to the backend. This is done by the `proxy` option in the `vite.config.ts` file.




## Find a bug? Have an idea?

If you find a bug in the source code or a mistake in the documentation, you can help me by submitting an issue in the [Issuetracker][issues-url]. Even better you can submit a Pull Request with a fix.

Furthermore if you have an idea for a new feature, feel free to submit an issue with a proposal for your new feature. Please add as much detail as possible to the issue description. This will help me to understand your idea and to discuss it with you.

**Thanks for making this project better!**




## Contact

Jeremiasz Zrolka - jeremiasz.zrolka@gmail.com

-   Twitter: [@jeremiasz_z][twitter-url]
-   Instagram: [@jeremiasz_z][instagram-url]
-   LinkedIn: [jeremiasz-zrolka][linkedin-url]



<!-- MARKDOWN LINKS & IMAGES -->
[repo]: https://github.com/bananensplit/tiss-cal-formatter
[contributors-shield]: https://img.shields.io/github/contributors/bananensplit/tiss-cal-formatter.svg
[contributors-url]: https://github.com/bananensplit/tiss-cal-formatter/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/bananensplit/tiss-cal-formatter.svg
[forks-url]: https://github.com/bananensplit/tiss-cal-formatter/network/members
[stars-shield]: https://img.shields.io/github/stars/bananensplit/tiss-cal-formatter.svg
[stars-url]: https://github.com/bananensplit/tiss-cal-formatter/stargazers
[issues-shield]: https://img.shields.io/github/issues/bananensplit/tiss-cal-formatter.svg
[issues-url]: https://github.com/bananensplit/tiss-cal-formatter/issues
[license-shield]: https://img.shields.io/github/license/bananensplit/tiss-cal-formatter.svg
[license-url]: https://github.com/bananensplit/tiss-cal-formatter/blob/master/LICENSE.md
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/jeremiasz-zrolka-78431021b
[twitter-url]: https://twitter.com/jeremiasz_z
[instagram-url]: https://instagram.com/jeremiasz_z

[import-ical-url]: https://help.hospitable.com/en/articles/4605516-how-can-i-add-the-ical-feed-to-the-calendar-on-my-device#for-google-calendar-on-web
[old-event-img]: /assets/old-event-img.png
[new-event-img]: /assets/new-event-img.png
