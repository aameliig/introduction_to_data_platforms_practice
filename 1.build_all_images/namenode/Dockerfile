FROM hadoop-base

ENV HDFS_CONF_dfs_namenode_name_dir=file:///hadoop/dfs/name

RUN mkdir -p /hadoop/dfs/name
VOLUME /hadoop/dfs/name

ADD run.sh /run.sh
RUN chmod a+x /run.sh

EXPOSE 9870
EXPOSE 9000

# check for service startup
HEALTHCHECK CMD curl -f http://localhost:9870/  || exit 1

CMD ["/run.sh"]
