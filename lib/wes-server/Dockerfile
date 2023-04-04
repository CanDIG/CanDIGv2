ARG toil_version
ARG wes_version

FROM candig/toil:$toil_version
LABEL maintainer=CanDIG
LABEL "candigv2"="wes-server"

RUN pip install -U pip && pip install --no-cache-dir wes-service

WORKDIR /root

#RUN apt-get update && \
  #DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential \
  #libssl-dev uuid-dev libgpgme11-dev libseccomp-dev \
  #pkg-config squashfs-tools cryptsetup

#ENV VERSION=1.13 OS=linux ARCH=amd64
#RUN wget -O /tmp/go${VERSION}.${OS}-${ARCH}.tar.gz https://dl.google.com/go/go${VERSION}.${OS}-${ARCH}.tar.gz && \
  #tar -C /usr/local -xzf /tmp/go${VERSION}.${OS}-${ARCH}.tar.gz

#ENV VERSION=3.5.2
#ENV GOPATH=/root/go
#ENV PATH=${GOPATH}/bin:/usr/local/go/bin:${PATH}

#RUN wget https://github.com/sylabs/singularity/releases/download/v${VERSION}/singularity-${VERSION}.tar.gz && \
  #tar xvf singularity-$VERSION.tar.gz && \
  #cd singularity && ./mconfig && cd ./builddir && make && make install

COPY mesos-wes.sh /root/mesos-wes.sh

RUN chmod 755 /root/mesos-wes.sh

#WORKDIR /root

ENTRYPOINT [ "wes-server" ]
