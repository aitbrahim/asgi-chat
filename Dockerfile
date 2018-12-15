FROM python:3

ENV PYTHONUNBUFFERED 1

# build-base
COPY requirements.txt /opt/pip/requirements.txt
RUN pip3 install -r /opt/pip/requirements.txt

ADD . /opt/app
WORKDIR /opt/app

EXPOSE 8000
