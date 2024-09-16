FROM hadoop-base

ENV HDFS_CONF_dfs_namenode_name_dir=file:///hadoop/dfs/data

RUN mkdir -p /hadoop/dfs/data
VOLUME /hadoop/dfs/data

ADD run.sh /run.sh
RUN chmod a+x /run.sh

EXPOSE 9864

CMD ["/run.sh"]
