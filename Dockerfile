#
# Dockerfile for pfmdb.
#
# Build with
#
#   docker build -t <name> .
#
# For example if building a local version, you could do:
#
#   docker build --build-arg UID=$UID -t local/pfms .
#
# In the case of a proxy (located at say 10.41.13.4:3128), do:
#
#    export PROXY="http://10.41.13.4:3128"
#    docker build --build-arg http_proxy=${PROXY} --build-arg UID=$UID -t local/pfmdb .
#
# To run an interactive shell inside this container, do:
#
#   docker run -ti --entrypoint /bin/bash local/pfmdb
#
# To pass an env var HOST_IP to the container, do:
#
#   docker run -ti -e HOST_IP=$(ip route | grep -v docker | awk '{if(NF==11) print $9}') --entrypoint /bin/bash local/pfmdb
#
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim

LABEL DEVELOPMENT="                                                         \
    docker run --rm -it                                                     \
    -p 2024:2024                                                            \
    -v $PWD/pfms:/app:ro  local/pfms /start-reload.sh                      \
"

ENV DEBIAN_FRONTEND=noninteractive


COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt && rm -v /tmp/requirements.txt
# RUN pip install tzlocal
# RUN pip install ipython
# RUN pip install pydantic
# RUN pip install tabulate
# RUN pip install rich
COPY ./pfms /app

RUN apt update                              && \
    apt-get install -y apt-transport-https  && \
    apt -y install dcmtk                    && \
    apt -y install ssh iputils-ping         && \
    apt -y install vim telnet netcat-traditional procps binutils

# Create the 'localuser' group with specified GID
RUN groupadd -g 1102 localuser

# Create the 'localuser' user with specified UID, add to the group, and create home directory
RUN useradd -u 7748 -g localuser -m -s /bin/bash localuser

# Grant sudo privileges to the 'localuser' user
RUN apt-get update && apt-get install -y sudo
RUN echo '%localuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER localuser

ENV PORT=2024
EXPOSE ${PORT}
