FROM python:3

ENV PYTHONUNBUFFERED 1

ADD . /opt/app
WORKDIR /opt/app

RUN pip install pipenv
RUN pipenv install --deploy --system

EXPOSE 8000
