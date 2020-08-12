FROM jupyter/base-notebook
LABEL maintainer="CanDIG <info@distributedgenomics.ca>"

ARG NB_USER="jovyan"
ARG NB_UID="1000"
ARG NB_GID="100"

# Configure environment
ENV CONDA_DIR=/opt/conda \
  SHELL=/bin/bash \
  NB_USER=${NB_USER} \
  NB_UID=${NB_UID} \
  NB_GID=${NB_GID} \
  LC_ALL=en_US.UTF-8 \
  LANG=en_US.UTF-8 \
  LANGUAGE=en_US.UTF-8 \
  PATH=${CONDA_DIR}/bin:$PATH \
  HOME=/home/${NB_USER}

USER root
WORKDIR /tmp

# Fix DL4006
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install all OS dependencies for fully functional notebook server
RUN apt-get update && apt-get install --quiet --yes \
  apt-transport-https \
  aria2 \
  build-essential \
  bzip2 \
  ca-certificates \
  ca-certificates-java \
  curl \
  default-jre \
  dvipng \
  emacs \
  ffmpeg \
  fonts-dejavu \
  fonts-liberation \
  g++ \
  gcc \
  gdebi-core \
  gfortran \
  git \
  gnupg2 \
  htop \
  inkscape \
  jed \
  libapparmor1 \
  libblas-dev \
  libcairo2-dev \
  libclang-dev \
  libcurl4-gnutls-dev \
  liblapack-dev \
  libpq-dev \
  librsvg2-bin \
  libsm6 \
  libsqlite3-dev \
  libssh2-1-dev \
  libssl-dev \
  libxext-dev \
  libxml2-dev \
  libxrender1 \
  lmodern \
  locales \
  lsb-release \
  make \
  nano \
  netcat \
  openjdk-11-jre-headless \
  pandoc \
  parallel \
  psmisc \
  python-dev \
  python3 \
  python3-dev \
  python3-pip \
  r-cran-* \
  samtools \
  software-properties-common \
  sudo \
  texlive-fonts-extra \
  texlive-fonts-recommended \
  texlive-latex-base \
  texlive-latex-extra \
  texlive-xetex \
  tzdata \
  unixodbc \
  unixodbc-dev \
  unzip \
  wget \
  && apt-get -y autoremove \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# install rstudio-server
ADD https://s3.amazonaws.com/rstudio-server/current.ver /tmp/ver
RUN wget https://download2.rstudio.org/server/bionic/amd64/rstudio-server-$(cut -f 1 -d - /tmp/ver)-amd64.deb && \
  gdebi -n rstudio-server-$(cut -f 1 -d - /tmp/ver)-amd64.deb

# docker-client support
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
  add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu `lsb_release -cs` stable"

RUN apt-get update && \
  apt-get install --quiet --yes docker-ce-cli && \
  rm -rf /var/lib/apt/lists/*

# Julia dependencies
# install Julia packages in /opt/julia instead of ${HOME}
ENV JULIA_DEPOT_PATH=/opt/julia \
  JULIA_PKGDIR=/opt/julia \
  JULIA_VERSION=1.4.1

# hadolint ignore=SC2046
RUN mkdir "/opt/julia-${JULIA_VERSION}" && \
  wget -q https://julialang-s3.julialang.org/bin/linux/x64/$(echo "${JULIA_VERSION}" | cut -d. -f 1,2)"/julia-${JULIA_VERSION}-linux-x86_64.tar.gz" && \
  echo "fd6d8cadaed678174c3caefb92207a3b0e8da9f926af6703fb4d1e4e4f50610a *julia-${JULIA_VERSION}-linux-x86_64.tar.gz" | sha256sum -c - && \
  tar xzf "julia-${JULIA_VERSION}-linux-x86_64.tar.gz" -C "/opt/julia-${JULIA_VERSION}" --strip-components=1 && \
  rm "/tmp/julia-${JULIA_VERSION}-linux-x86_64.tar.gz"
RUN ln -fs /opt/julia-*/bin/julia /usr/local/bin/julia

# Show Julia where conda libraries are \
RUN mkdir /etc/julia && \
  echo "push!(Libdl.DL_LOAD_PATH, \"${CONDA_DIR}/lib\")" >> /etc/julia/juliarc.jl && \
  # Create JULIA_PKGDIR \
  mkdir "${JULIA_PKGDIR}" && \
  chown "${NB_USER}" "${JULIA_PKGDIR}" && \
  fix-permissions "${JULIA_PKGDIR}"

# Spark dependencies
ENV APACHE_SPARK_VERSION=3.0.0 \
  HADOOP_VERSION=3.2

# hadolint ignore=SC2046
RUN wget -q $(wget -qO- https://www.apache.org/dyn/closer.lua/spark/spark-${APACHE_SPARK_VERSION}/spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz\?as_json | \
  python -c "import sys, json; content=json.load(sys.stdin); print(content['preferred']+content['path_info'])") && \
  echo "BFE45406C67CC4AE00411AD18CC438F51E7D4B6F14EB61E7BF6B5450897C2E8D3AB020152657C0239F253735C263512FFABF538AC5B9FFFA38B8295736A9C387 *spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" | sha512sum -c - && \
  tar xzf "spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" -C /usr/local --owner root --group root --no-same-owner && \
  rm "spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz"

RUN ln -s "spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}" /usr/local/spark

# Configure Spark
ENV SPARK_HOME=/usr/local/spark
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9-src.zip \
  SPARK_OPTS="--driver-java-options=-Xms1024M --driver-java-options=-Xmx4096M --driver-java-options=-Dlog4j.logLevel=info" \
  PATH=$PATH:$SPARK_HOME/bin

# Fix for devtools https://github.com/conda-forge/r-devtools-feedstock/issues/4
RUN ln -s /bin/tar /bin/gtar

# RSpark config
#ENV R_LIBS_USER $SPARK_HOME/R/lib
#RUN fix-permissions $R_LIBS_USER

RUN mkdir /notebooks /library /download

RUN wget -O docker-ce-cli.deb \
  https://download.docker.com/linux/ubuntu/dists/xenial/pool/stable/amd64/docker-ce-cli_19.03.9~3-0~ubuntu-xenial_amd64.deb && \
  dpkg -i docker-ce-cli.deb && \
  groupadd docker

RUN chown -R ${NB_UID}:${NB_GID} /notebooks /library /download && \
  echo "${NB_USER} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook && \
  usermod -aG docker ${NB_USER}

USER ${NB_UID}
WORKDIR ${HOME}

# R packages including IRKernel which gets installed globally.
RUN conda install --quiet --yes \
  'r-ggplot2=3.3.*' \
  'r-irkernel=1.1.*' \
  'r-rcurl=1.98.*' \
  'r-sparklyr=1.2.*' \
  'r-base=3.6.3' \
  'r-caret=6.*' \
  'r-crayon=1.3*' \
  'r-devtools=2.3.*' \
  'r-forecast=8.12.*' \
  'r-hexbin=1.28.*' \
  'r-htmltools=0.4.*' \
  'r-htmlwidgets=1.5.*' \
  'r-nycflights13=1.0.*' \
  'r-plyr=1.8.*' \
  'r-randomforest=4.6.*' \
  'r-reshape2=1.4.*' \
  'r-rmarkdown=2.1.*' \
  'r-rodbc=1.3.*' \
  'r-rsqlite=2.2.*' \
  'r-shiny=1.4.*' \
  'r-tidymodels=0.1.*' \
  'r-tidyverse=1.3.*' \
  'rpy2=3.1.*' \
  'unixodbc=2.3.*' \
  && conda clean --all -f -y && \
  fix-permissions ${CONDA_DIR} && \
  fix-permissions /home/${NB_USER}

# Install e1071 R package (dependency of the caret R package)
RUN conda install --quiet --yes r-e1071

# Add Julia packages. Only add HDF5 if this is not a test-only build since
# it takes roughly half the entire build time of all of the images on Travis
# to add this one package and often causes Travis to timeout.
#
# Install IJulia as jovyan and then move the kernelspec out
# to the system share location. Avoids problems with runtime UID change not
# taking effect properly on the .local folder in the jovyan home dir.
RUN julia -e 'import Pkg; Pkg.update()' && \
  (test $TEST_ONLY_BUILD || julia -e 'import Pkg; Pkg.add("HDF5")') && \
  julia -e "using Pkg; pkg\"add IJulia\"; pkg\"precompile\"" && \
  # move kernelspec out of home \
  mv "${HOME}/.local/share/jupyter/kernels/julia"* "${CONDA_DIR}/share/jupyter/kernels/" && \
  chmod -R go+rx "${CONDA_DIR}/share/jupyter" && \
  rm -rf "${HOME}/.local" && \
  fix-permissions "${JULIA_PKGDIR}" "${CONDA_DIR}/share/jupyter"

# Install Python 3 packages
# Remove pyqt and qt pulled in for matplotlib since we're only ever going to
# use notebook-friendly backends in these images
RUN conda install --quiet --yes \
  'beautifulsoup4=4.9.*' \
  'conda-forge::blas=*=openblas' \
  'bokeh=2.1.*' \
  'bottleneck=1.3.*' \
  'cloudpickle=1.5.*' \
  'cython=0.29.*' \
  'dask=2.20.*' \
  'dill=0.3.*' \
  'h5py=2.10.*' \
  'hdf5=1.10.*' \
  'ipywidgets=7.5.*' \
  'ipympl=0.5.*'\
  'matplotlib-base=3.2.*' \
  # numba update to 0.49 fails resolving deps.
  'numba=0.48.*' \
  'numexpr=2.7.*' \
  'pandas=1.0.*' \
  'patsy=0.5.*' \
  'protobuf=3.12.*' \
  'pyarrow' \
  'pytables=3.6.*' \
  'scikit-image=0.17.*' \
  'scikit-learn=0.23.*' \
  'scipy=1.5.*' \
  'seaborn=0.10.*' \
  'sqlalchemy=1.3.*' \
  'statsmodels=0.11.*' \
  'sympy=1.6.*' \
  'vincent=0.4.*' \
  'widgetsnbextension=3.5.*'\
  'xlrd=1.2.*' \
  && \
  conda clean --all -f -y && \
  # Activate ipywidgets extension in the environment that runs the notebook server
  jupyter nbextension enable --py widgetsnbextension --sys-prefix && \
  # Also activate ipywidgets extension for JupyterLab
  # Check this URL for most recent compatibilities
  # https://github.com/jupyter-widgets/ipywidgets/tree/master/packages/jupyterlab-manager
  jupyter labextension install @jupyter-widgets/jupyterlab-manager@^2.0.0 --no-build && \
  jupyter labextension install @bokeh/jupyter_bokeh@^2.0.0 --no-build && \
  jupyter labextension install jupyter-matplotlib@^0.7.2 --no-build && \
  jupyter lab build -y && \
  jupyter lab clean -y && \
  npm cache clean --force && \
  rm -rf "/home/${NB_USER}/.cache/yarn" && \
  rm -rf "/home/${NB_USER}/.node-gyp" && \
  fix-permissions "${CONDA_DIR}" && \
  fix-permissions "/home/${NB_USER}"

# Install facets which does not have a pip or conda package at the moment
RUN git clone https://github.com/PAIR-code/facets.git && \
  jupyter nbextension install facets/facets-dist/ --sys-prefix && \
  rm -rf /tmp/facets && \
  fix-permissions "${CONDA_DIR}" && \
  fix-permissions "/home/${NB_USER}"

# Import matplotlib the first time to build the font cache.
ENV XDG_CACHE_HOME="/home/${NB_USER}/.cache/"

RUN MPLBACKEND=Agg python -c "import matplotlib.pyplot" && \
  fix-permissions "/home/${NB_USER}"

# Install Tensorflow
RUN pip install --quiet --no-cache-dir \
  'tensorflow==2.2.0' && \
  fix-permissions "${CONDA_DIR}" && \
  fix-permissions "/home/${NB_USER}"

# Spylon-kernel
RUN conda install --quiet --yes 'spylon-kernel=0.4*' && \
  conda clean --all -f -y && \
  python -m spylon_kernel install --sys-prefix && \
  rm -rf "/home/${NB_USER}/.local" && \
  fix-permissions "${CONDA_DIR}" && \
  fix-permissions "/home/${NB_USER}"

COPY demo /notebooks/demo
