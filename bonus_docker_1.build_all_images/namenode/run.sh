#!/bin/bash

if [ "`ls -A /hadoop/dfs/name`" == "" ]; then
  # format hdfs if first start
  $HADOOP_HOME/bin/hdfs --config $HADOOP_CONF_DIR namenode -format
fi

$HADOOP_HOME/bin/hdfs --config $HADOOP_CONF_DIR namenode
