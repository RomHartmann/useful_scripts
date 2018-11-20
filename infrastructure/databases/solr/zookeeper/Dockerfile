FROM openjdk:8

USER root

#Install Python, pip and dev dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip

#Install Zookeeper
ENV ZOOKEEPER_VERSION 3.4.11
RUN wget -q -O - http://apache.mirrors.pair.com/zookeeper/zookeeper-${ZOOKEEPER_VERSION}/zookeeper-${ZOOKEEPER_VERSION}.tar.gz | tar -xzf - -C /opt
RUN mv /opt/zookeeper-${ZOOKEEPER_VERSION} /opt/zookeeper

# Install Python Packages
COPY /code/requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt

# Run the configuration & runnerscript
RUN mkdir -p /code
COPY /code /code/
WORKDIR /code

ENV log_level DEBUG
CMD ["python3", "run-zookeeper.py"]