ARG BASE_CONTAINER=jupyter/base-notebook
FROM $BASE_CONTAINER

LABEL maintainer="CanDIG <info@distributedgenomics.ca"

USER root

# Install all OS dependencies for fully functional notebook server
RUN apt-get update && apt-get install --quiet --yes \
  build-essential \
  emacs \
  git \
  inkscape \
  jed \
  libsm6 \
  libxext-dev \
  libxrender1 \
  lmodern \
  netcat \
  pandoc \
  python-dev \
  python3 \
  python3-pip \
  python3-dev \
  wget \
  tzdata \
  libcairo2-dev \
  texlive-fonts-extra \
  texlive-fonts-recommended \
  texlive-generic-recommended \
  texlive-latex-base \
  texlive-latex-extra \
  texlive-xetex \
  unzip \
  nano \
  htop \
  libssl-dev \
  libssl1.0.0 \
  default-jre \
  gnupg2 \
  curl \
  apt-transport-https \
  ca-certificates \
  software-properties-common \
  fonts-dejavu \
  tzdata \
  unixodbc \
  unixodbc-dev \
  r-cran-rodbc \
  gfortran \
  ffmpeg \
  parallel \
  aria2 \
  samtools \
  gcc && \
  rm -rf /var/lib/apt/lists/*

# docker-client support
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
  add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu `lsb_release -cs` stable"

RUN apt-get update && \
  apt-get install --quiet --yes docker-ce docker-ce-cli containerd.io && \
  rm -rf /var/lib/apt/lists/* && \
  usermod -aG docker $NB_USER

USER $NB_UID

# R packages including IRKernel which gets installed globally.
RUN conda install --quiet --yes \
  'rpy2=2.9*' \
  'r-base=3.5.1' \
  'r-irkernel=0.8*' \
  'r-rodbc=1.3*' \
  'unixodbc=2.3.*' \
  'r-plyr=1.8*' \
  'r-devtools=1.13*' \
  'r-tidyverse=1.2*' \
  'r-shiny=1.2*' \
  'r-rmarkdown=1.11*' \
  'r-forecast=8.2*' \
  'r-rsqlite=2.1*' \
  'r-reshape2=1.4*' \
  'r-nycflights13=1.0*' \
  'r-caret=6.0*' \
  'r-rcurl=1.95*' \
  'r-crayon=1.3*' \
  'r-randomforest=4.6*' \
  'r-htmltools=0.3*' \
  'r-sparklyr=0.9*' \
  'r-htmlwidgets=1.2*' \
  'r-hexbin=1.27*' && \
  conda clean -tipsy && \
  fix-permissions $CONDA_DIR && \
  fix-permissions /home/$NB_USER

# Install Python 3 packages
# Remove pyqt and qt pulled in for matplotlib since we're only ever going to
# use notebook-friendly backends in these images
RUN conda install --quiet --yes \
  'conda-forge::blas=*=openblas' \
  'ipywidgets=7.4*' \
  'pandas=0.23*' \
  'numexpr=2.6*' \
  'matplotlib=2.2*' \
  'scipy=1.1*' \
  'seaborn=0.9*' \
  'scikit-learn=0.20*' \
  'scikit-image=0.14*' \
  'sympy=1.1*' \
  'cython=0.28*' \
  'patsy=0.5*' \
  'statsmodels=0.9*' \
  'cloudpickle=0.5*' \
  'dill=0.2*' \
  'dask=1.1.*' \
  'dask-jobqueue=0.4.*' \
  'dask-ml=0.11.*' \
  'numba=0.38*' \
  'bokeh=0.13*' \
  'sqlalchemy=1.2*' \
  'hdf5=1.10*' \
  'h5py=2.7*' \
  'vincent=0.4.*' \
  'beautifulsoup4=4.6.*' \
  'protobuf=3.*' \
  'xlrd'  && \
  conda remove --quiet --yes --force qt pyqt && \
  conda clean -tipsy && \
  # Activate ipywidgets extension in the environment that runs the notebook server
  jupyter nbextension enable --py widgetsnbextension --sys-prefix && \
  # Also activate ipywidgets extension for JupyterLab
  # Check this URL for most recent compatibilities
  # https://github.com/jupyter-widgets/ipywidgets/tree/master/packages/jupyterlab-manager
  jupyter labextension install @jupyter-widgets/jupyterlab-manager@^0.38.1 && \
  jupyter labextension install jupyterlab_bokeh@0.6.3 && \
  npm cache clean --force && \
  rm -rf $CONDA_DIR/share/jupyter/lab/staging && \
  rm -rf /home/$NB_USER/.cache/yarn && \
  rm -rf /home/$NB_USER/.node-gyp && \
  fix-permissions $CONDA_DIR && \
  fix-permissions /home/$NB_USER

# Install facets which does not have a pip or conda package at the moment
#RUN cd /tmp && \
  #git clone https://github.com/PAIR-code/facets.git && \
  #cd facets && \
  #jupyter nbextension install facets-dist/ --sys-prefix && \
  #cd && \
  #rm -rf /tmp/facets && \
  #fix-permissions $CONDA_DIR && \
  #fix-permissions /home/$NB_USER

# Import matplotlib the first time to build the font cache.
#ENV XDG_CACHE_HOME /home/$NB_USER/.cache/
#RUN MPLBACKEND=Agg python -c "import matplotlib.pyplot" && \
#fix-permissions /home/$NB_USER

# Install Tensorflow
#RUN conda install --quiet --yes \
  #'tensorflow=1.12*' \
  #'keras=2.2*' && \
  #conda clean -tipsy && \
  #fix-permissions $CONDA_DIR && \
  #fix-permissions /home/$NB_USER

# Install BioJupies Packages
#COPY requirements.R /home/jovyan/
#RUN Rscript /home/jovyan/requirements.R

#COPY requirements.txt /home/jovyan/
#RUN pip3 install --user -r requirements.txt

USER root

RUN mkdir /notebooks /library /download

#COPY download_libraries.py /home/jovyan/
#RUN python3 /home/jovyan/download_libraries.py

COPY demo /notebooks/demo

RUN chown -R $NB_UID:$NB_GID /notebooks /library /download

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID

#RUN jupyterhub token jovyan

#RUN bash /notebooks/demo/install-demos.sh
