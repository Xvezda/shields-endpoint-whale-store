FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7-alpine3.8

RUN apk update
RUN apk add build-base

COPY . /app
WORKDIR /app
RUN pip install --upgrade setuptools pip
RUN pip install -r requirements.txt

EXPOSE 80
