FROM python:alpine
LABEL maintainer=CanDIG

ARG dos_version
ARG htsget_version

WORKDIR /root

RUN apk update
#RUN apk add python py-pip
COPY demo.py .

RUN pip3 install ga4gh-dos-schemas==$dos_version htsget==$htsget_version

#ENTRYPOINT ["python3", "demo.py"]
