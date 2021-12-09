FROM python:3.9.6-slim-buster
RUN apt-get update

RUN pip install ping3

COPY HostScan.py /bin/runner/files/
COPY services.csv /bin/runner/files/

WORKDIR /bin/runner/files

ENTRYPOINT ["python3", "HostScan.py"]