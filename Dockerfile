FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7-alpine3.8

RUN apk update
RUN apk add build-base

RUN pip install --upgrade setuptools pip

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 80
