FROM solr:7.2

#We need to become the root user to setup the environment
USER root

RUN mkdir -p /code
RUN mkdir -p /data
WORKDIR /code
COPY /code /code/

#Copy over our custom configs
RUN cp /code/log4j.properties /opt/solr/server/resources/log4j.properties

# Copy over extra libraries
COPY /libs/jts-1.14/lib/* /opt/solr/server/solr-webapp/webapp/WEB-INF/lib/

#Reset file permissions
RUN chown -R solr:solr /opt/solr

#We need our solr user to have the ability to sudo
RUN apt-get update && apt-get install -y sudo
RUN echo "solr ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

#Switch back to non-privaledged user
USER solr

#Execute our custom start script
CMD ["/code/start-solr.sh"]