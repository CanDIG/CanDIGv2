ARG toil_version
ARG wes_version

FROM candig/toil:$toil_version
LABEL maintainer=CanDIG

RUN pip install wes-service

WORKDIR /root

RUN apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential \
  libssl-dev uuid-dev libgpgme11-dev libseccomp-dev \
  pkg-config squashfs-tools cryptsetup

ENV VERSION=1.12.6 OS=linux ARCH=amd64
RUN wget -O /tmp/go${VERSION}.${OS}-${ARCH}.tar.gz https://dl.google.com/go/go${VERSION}.${OS}-${ARCH}.tar.gz && \
  tar -C /usr/local -xzf /tmp/go${VERSION}.${OS}-${ARCH}.tar.gz && \
  echo 'export GOPATH=${HOME}/go' >> ~/.bashrc && \
  echo 'export PATH=/usr/local/go/bin:${PATH}:${GOPATH}/bin' >> ~/.bashrc

ENV VERSION=3.3.0
ENV GOPATH=/root/go
ENV PATH=$GOPATH/bin:/usr/local/go/bin:$PATH

RUN wget https://github.com/singularityware/singularity/releases/download/v$VERSION/singularity-$VERSION.tar.gz && \
  tar xvf singularity-$VERSION.tar.gz && \
  cd singularity && ./mconfig && cd ./builddir && make && make install
