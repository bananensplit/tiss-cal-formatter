FROM nikolaik/python-nodejs:python3.10-nodejs19

USER pn
WORKDIR /home/pn/app

# ARGs
ARG BASE_URL="/"

# ENVs
ENV MONGO_CONNECTION_STRING=""
ENV REDIS_HOST=""
ENV REDIS_PORT="6379"
ENV REDIS_PASSWORD=""


# SETUP THE FRONTEND
WORKDIR /home/pn/app/frontend

COPY frontend/package.json ./
COPY frontend/vite.config.js ./
# COPY frontend/public ./public
COPY frontend/src ./src
COPY frontend/index.html ./

RUN npm install

RUN npm run build -- --base ${BASE_URL}


# SETUP THE BACKEND
WORKDIR /home/pn/app/backend

COPY backend/requirements.txt ./
COPY backend/main.py ./
COPY backend/UserHandler.py ./
COPY backend/TissCalHandler.py ./
COPY backend/MyCalendar.py ./
COPY backend/Lva.py ./
COPY backend/MyMongoClient.py ./
COPY backend/MyHTTPException.py ./

RUN mkdir models
COPY backend/models/ErrorResponse.py ./models
COPY backend/models/ResponseBase.py ./models
COPY backend/models/TissCalModels.py ./models
COPY backend/models/UserModels.py ./models

RUN mkdir resources
COPY backend/resources ./resources

RUN pip install --no-cache-dir -r requirements.txt


RUN touch .env
RUN echo "BASE_URL=\"${BASE_URL}\"" >> .env
RUN echo "MONGO_CONNECTION_STRING=\"${MONGO_CONNECTION_STRING}\"" >> .env
RUN echo "REDIS_HOST=\"${REDIS_HOST}\"" >> .env
RUN echo "REDIS_PORT=\"${REDIS_PORT}\"" >> .env
RUN echo "REDIS_PASSWORD=\"${REDIS_PASSWORD}\"" >> .env


# EXPOSE PORT 80
EXPOSE 80


# RUN THE APP
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]