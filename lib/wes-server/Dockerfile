ARG toil_version

FROM candig/toil:$toil_version
LABEL maintainer=CanDIG

RUN pip install wes-service==${WES_VERSION:-3.3}
