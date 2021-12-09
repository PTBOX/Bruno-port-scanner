FROM python:3.9.6-slim-buster
RUN apt-get update

RUN pip install docker netaddr six

COPY . /bin/runner/files/

WORKDIR /bin/runner/files

ENTRYPOINT ["python3", "main.py"]