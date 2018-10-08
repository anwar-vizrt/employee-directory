FROM ubuntu:18.04
MAINTAINER Anwarul Islam <sk.anwarul.islam@gmail.com>

# Install minimal apt stuff needed for apt to work at all
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        apt-transport-https \
        curl \
        make \
        unzip \
	    python3-pip \
        && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

WORKDIR /srv/employee-directory

COPY . .

RUN pip3 install -r requirements.txt

CMD python3 api/directory.py





