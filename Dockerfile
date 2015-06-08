FROM python:3.4

ADD requirements.txt requirements.txt
ADD requirements-dev.txt requirements-dev.txt

RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt
