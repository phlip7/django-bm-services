# syntax=docker/dockerfile:1
FROM python:3.9
ENV PYTHONUNBUFFERED=1

#COPY requirements.txt /code/
COPY . /code/
WORKDIR /code
RUN pip install -r requirements.txt
RUN python manage.py migrate