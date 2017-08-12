FROM python:latest
MAINTAINER Andis Cirulis "andis.cirulis@whitedigital.eu"

#ENV PYTHONUNBUFFERED 1

#RUN apt-get install -y tk-dev python3-tk
#RUN apt-get install -y python3-pyqt5
# RUN pip install pyqt5

RUN apt-get update \
&& apt-get install -y vim

WORKDIR /root
COPY  requirements.txt /root/
RUN pip install -r requirements.txt

#lets wait for matplotlib 2.0.1 before this will fixed
ENV MPLBACKEND TkAgg

#lets install yolo
RUN git clone https://github.com/pjreddie/darknet \
&& cd darknet \
&& make


ENTRYPOINT  ["bash"]
