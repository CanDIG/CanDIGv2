# This Dockerfile should be located inside the root level of the submodule

# These arguments are picked up from the environment and passed in from the docker-compose file
ARG venv_python
ARG alpine_version
FROM python:${venv_python}-alpine${alpine_version}

LABEL Maintainer="CanDIG Project"

# Copy module repo as needed
COPY . /app/<module_name>

# Alternatively, clone it:
# RUN git clone https://github.com/candig/<module_name>.git

# Set the working directory
WORKDIR /app/<module_name>

# Run necessary steps to implement module
# uncomment and add as needed:
# RUN apt-get update
# RUN apt-get -y install gcc libc-dev
# RUN pip install --no-cache-dir -r requirements.txt && flask db upgrade

# Run the model service server
# uncomment and add as needed:
# ENTRYPOINT ["flask", "run"]
