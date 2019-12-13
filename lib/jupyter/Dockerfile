FROM jupyter/base-notebook
LABEL maintainer="CanDIG <info@distributedgenomics.ca>"

ARG NB_USER="jovyan" \
  NB_UID="1000" \
  NB_GID="100"

# Configure environment
ENV CONDA_DIR=/opt/conda \
  SHELL=/bin/bash \
  NB_USER=$NB_USER \
  NB_UID=$NB_UID \
  NB_GID=$NB_GID \
  LC_ALL=en_US.UTF-8 \
  LANG=en_US.UTF-8 \
  LANGUAGE=en_US.UTF-8 \
  PATH=$CONDA_DIR/bin:$PATH \
  HOME=/home/$NB_USER

USER root
WORKDIR /root

# Install all OS dependencies for fully functional notebook server
RUN apt-get update && apt-get install --quiet --yes \
  apt-transport-https \
  aria2 \
  build-essential \
  bzip2 \
  ca-certificates \
  curl \
  default-jre \
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
  libmariadb-client-lgpl-dev \
  libpq-dev \
  librsvg2-bin \
  libsm6 \
  libsqlite3-dev \
  libssh2-1-dev \
  libssl-dev \
  libssl1.0.0 \
  libxext-dev \
  libxml2-dev \
  libxrender1 \
  lmodern \
  locales \
  lsb-release \
  make \
  nano \
  netcat \
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
  texlive-generic-recommended \
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
  add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu `lsb_release -cs` stable"

RUN apt-get update && \
  apt-get install --quiet --yes docker-ce-cli && \
  rm -rf /var/lib/apt/lists/*

# Julia dependencies
# install Julia packages in /opt/julia instead of $HOME
ENV JULIA_DEPOT_PATH=/opt/julia \
  JULIA_PKGDIR=/opt/julia \
  JULIA_VERSION=1.2.0

RUN mkdir /opt/julia-${JULIA_VERSION} && \
  cd /tmp && \
  wget -q https://julialang-s3.julialang.org/bin/linux/x64/`echo ${JULIA_VERSION} \
    | cut -d. -f 1,2`/julia-${JULIA_VERSION}-linux-x86_64.tar.gz && \
  echo "926ced5dec5d726ed0d2919e849ff084a320882fb67ab048385849f9483afc47 *julia-${JULIA_VERSION}-linux-x86_64.tar.gz" \
    | sha256sum -c - && \
  tar xzf julia-${JULIA_VERSION}-linux-x86_64.tar.gz -C /opt/julia-${JULIA_VERSION} --strip-components=1 && \
  rm /tmp/julia-${JULIA_VERSION}-linux-x86_64.tar.gz && \
  ln -fs /opt/julia-*/bin/julia /usr/local/bin/julia

# Show Julia where conda libraries are \
RUN mkdir /etc/julia && \
  echo "push!(Libdl.DL_LOAD_PATH, \"$CONDA_DIR/lib\")" >> /etc/julia/juliarc.jl && \
  mkdir $JULIA_PKGDIR && \
  chown $NB_USER $JULIA_PKGDIR && \
  fix-permissions $JULIA_PKGDIR

# Fix for devtools https://github.com/conda-forge/r-devtools-feedstock/issues/4
RUN ln -s /bin/tar /bin/gtar

# RSpark config
#ENV R_LIBS_USER $SPARK_HOME/R/lib
#RUN fix-permissions $R_LIBS_USER

RUN mkdir /notebooks /library /download
COPY demo /notebooks/demo

RUN chown -R $NB_UID:$NB_GID /notebooks /library /download && \
  echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook && \
  usermod -aG docker $NB_USER

USER $NB_UID
WORKDIR $HOME

# Install conda as jovyan and check the md5 sum provided on the download site
#ENV MINICONDA_VERSION=4.6.14 \
  #CONDA_VERSION=4.7.5

# R packages including IRKernel which gets installed globally.
RUN conda install --quiet --yes \
  'r-ggplot2=3.2*' \
  'r-irkernel=1.0*' \
  'r-rcurl=1.95*' \
  'r-sparklyr=1.0*' \
  'r-base=3.6.1' \
  'r-caret=6.0*' \
  'r-crayon=1.3*' \
  'r-devtools=2.1*' \
  'r-forecast=8.7*' \
  'r-hexbin=1.27*' \
  'r-htmltools=0.3*' \
  'r-htmlwidgets=1.3*' \
  'r-nycflights13=1.0*' \
  'r-plyr=1.8*' \
  'r-randomforest=4.6*' \
  'r-rcurl=1.95*' \
  'r-reshape2=1.4*' \
  'r-rmarkdown=1.14*' \
  'r-rodbc=1.3*' \
  'r-rsqlite=2.1*' \
  'r-shiny=1.3*' \
  'r-tidyverse=1.2*' \
  'rpy2=2.9*' \
  'unixodbc=2.3.*' \
  && conda clean --all -f -y && \
  fix-permissions $CONDA_DIR && \
  fix-permissions /home/$NB_USER

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
  julia -e "using Pkg; pkg\"add Gadfly RDatasets IJulia InstantiateFromURL\"; pkg\"precompile\"" && \
  # move kernelspec out of home \
  mv $HOME/.local/share/jupyter/kernels/julia* $CONDA_DIR/share/jupyter/kernels/ && \
  chmod -R go+rx $CONDA_DIR/share/jupyter && \
  rm -rf $HOME/.local && \
  fix-permissions $JULIA_PKGDIR $CONDA_DIR/share/jupyter

# Install Python 3 packages
# Remove pyqt and qt pulled in for matplotlib since we're only ever going to
# use notebook-friendly backends in these images
RUN conda install --quiet --yes \
  'conda-forge::blas=*=openblas' \
  'conda-forge::jupyter_nbextensions_configurator' \
  'beautifulsoup4=4.8.*' \
  'bokeh=1.3*' \
  'cloudpickle=1.2*' \
  'cython=0.29*' \
  'dask-jobqueue=0.4.*' \
  'dask-ml=0.11.*' \
  'dask=2.2.*' \
  'dill=0.3*' \
  'h5py=2.9*' \
  'hdf5=1.10*' \
  'ipywidgets=7.5*' \
  'matplotlib-base=3.1*' \
  'numba=0.45*' \
  'numexpr=2.6*' \
  'pandas=0.25*' \
  'patsy=0.5*' \
  'protobuf=3.9.*' \
  'scikit-image=0.15*' \
  'scikit-learn=0.21*' \
  'scipy=1.3*' \
  'seaborn=0.9*' \
  'sqlalchemy=1.3*' \
  'statsmodels=0.10*' \
  'sympy=1.4*' \
  'vincent=0.4.*' \
  'xlrd' \
  && conda clean --all -f -y && \
  # Activate ipywidgets extension in the environment that runs the notebook server
  jupyter nbextension enable --py widgetsnbextension --sys-prefix && \
  # Also activate ipywidgets extension for JupyterLab
  # Check this URL for most recent compatibilities
  # https://github.com/jupyter-widgets/ipywidgets/tree/master/packages/jupyterlab-manager
  jupyter labextension install @jupyter-widgets/jupyterlab-manager@^1.0.0 && \
  jupyter labextension install jupyterlab_bokeh@1.0.0 && \
  jupyter lab build && \
  npm cache clean --force && \
  rm -rf $CONDA_DIR/share/jupyter/lab/staging && \
  rm -rf /home/$NB_USER/.cache/yarn && \
  rm -rf /home/$NB_USER/.node-gyp && \
  fix-permissions $CONDA_DIR && \
  fix-permissions /home/$NB_USER

# Install facets which does not have a pip or conda package at the moment
RUN cd /tmp && \
  git clone https://github.com/PAIR-code/facets.git && \
  cd facets && \
  jupyter nbextension install facets-dist/ --sys-prefix && \
  cd && \
  rm -rf /tmp/facets && \
  fix-permissions $CONDA_DIR && \
  fix-permissions /home/$NB_USER

# Import matplotlib the first time to build the font cache.
ENV XDG_CACHE_HOME /home/$NB_USER/.cache/
RUN MPLBACKEND=Agg python -c "import matplotlib.pyplot" && \
  fix-permissions /home/$NB_USER

# Install Tensorflow
RUN conda install --quiet --yes \
  'tensorflow=2.0.0' \
  'keras=2.3*' && \
  conda clean --all -f -y && \
  fix-permissions $CONDA_DIR && \
  fix-permissions /home/$NB_USER

# Apache Toree kernel
RUN pip install --no-cache-dir \
  https://dist.apache.org/repos/dist/release/incubator/toree/0.3.0-incubating/toree-pip/toree-0.3.0.tar.gz \
  && \
  jupyter toree install --sys-prefix && \
  rm -rf /home/$NB_USER/.local && \
  fix-permissions $CONDA_DIR && \
  fix-permissions /home/$NB_USER

# Spylon-kernel
RUN conda install --quiet --yes 'spylon-kernel=0.4*' && \
  conda clean --all -f -y && \
  python -m spylon_kernel install --sys-prefix && \
  rm -rf /home/$NB_USER/.local && \
  fix-permissions $CONDA_DIR && \
  fix-permissions /home/$NB_USER

