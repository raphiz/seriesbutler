FROM python:3.4

# Create new user "user" - to prevent user id issues
RUN groupadd -g 1000 user
RUN useradd --home /src -u 1000 -g 1000 -M user
WORKDIR /src

RUN apt-get update
RUN apt-get install libav-tools -y

ADD requirements.txt requirements.txt
ADD requirements-dev.txt requirements-dev.txt

RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt
