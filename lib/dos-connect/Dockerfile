FROM python:alpine
LABEL maintainer=CanDIG

WORKDIR /root

RUN apk update

RUN apk add alpine-sdk musl-dev libffi-dev openssl-dev ethtool git linux-headers

RUN git clone https://github.com/ohsu-comp-bio/dos_connect.git

#RUN pip install connexion==1.4.2
#RUN pip install -r dos_connect/requirements.txt
RUN pip install -r dos_connect/dos_connect/server/requirements.txt

