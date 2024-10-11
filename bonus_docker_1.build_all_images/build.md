# Создание образов

**Шаг 1.** Создаем отдельную папку для нашего проекта, чтобы было удобнее работать. Набираем в консоли:
```
  mkdir hadoop
  cd hadoop
```

Аналогично, создаем папки, отвечающие за образы: 
```
  mkdir base
  cd ../
  mkdir namenode
  cd ../
  mkdir datanode
  cd ../
```

**Шаг 2.** Заходим в **base** (```cd ./base```). С помощью редактора, например, nvim **создаем Dockerfile**.
Наш файл целиком приложен в этой папке, поясним некоторые его строчки:

``` FROM ubuntu:22.04  # версия ubuntu```

```
# устанавливаем 8ую версию java - подходит для hadoop
# флаг -headless позволяет не скачивать интерфейс, а только самое нужное

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      openjdk-8-jdk-headless \
      net-tools \
      curl \
      netcat \
      gnupg \
      libsnappy-dev \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
```

```
# установка HADOOP версии 3.3.6
# вставили url с официального сайта, скачали, распаковали

ENV HADOOP_VERSION 3.3.6
ENV HADOOP_URL https://www.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz
RUN curl -fSL "$HADOOP_URL" -o /tmp/hadoop.tar.gz \
    && tar -xvf /tmp/hadoop.tar.gz -C /opt/ \
    && rm /tmp/hadoop.tar.gz*

RUN mkdir /opt/hadoop-$HADOOP_VERSION/logs
```

```
# создаем пользователя hadoop, из под которого будем запускаться
# прописываем ему доступ к среде
# указываем, что стартуем под hadoop
 
RUN useradd -ms /bin/bash hadoop && usermod -aG sudo hadoop 
RUN chown -R hadoop:hadoop /opt/hadoop-$HADOOP_VERSION
ENV USER=hadoop
```

```
# настраиваем переменные среды

ENV HADOOP_HOME=/opt/hadoop-$HADOOP_VERSION
ENV HADOOP_INSTALL=$HADOOP_HOME
ENV HADOOP_MAPRED_HOME=$HADOOP_HOME
ENV HADOOP_COMMON_HOME=$HADOOP_HOME
ENV HADOOP_HDFS_HOME=$HADOOP_HOME
ENV YARN_HOME=$HADOOP_HOME
ENV HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
ENV PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
ENV HADOOP_OPTS="-Djava.library.path=$HADOOP_HOME/lib/native"
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
```

Далее, сделаем удобный **скрипт для запуска build.sh**

```docker build -t hadoop-base .```


**Шаг 3.** Теперь заходим в **namenode**. С помощью редактора, например, nvim **создаем Dockerfile**.
Наш файл целиком приложен в этой папке, поясним некоторые его строчки:

```
FROM hadoop-base

# создаем каталог для namenode - там хранятся данные

ENV HDFS_CONF_dfs_namenode_name_dir=file:///hadoop/dfs/name

RUN mkdir -p /hadoop/dfs/name
VOLUME /hadoop/dfs/name

# добавляем скрипт run и делаем его исполняемым

ADD run.sh /run.sh
RUN chmod a+x /run.sh

EXPOSE 9870
EXPOSE 9000

# проверка успешного запуска
HEALTHCHECK CMD curl -f http://localhost:9870/  || exit 1

CMD ["/run.sh"]
```


**В папке приложен скрипт run.sh.** Если стартуем в первый раз - запускаем форматирование, иначе обычный старт.

Аналогично, сделаем удобный **скрипт для запуска build.sh**

```docker build -t hadoop-namenode .```




**Шаг 4.** Аналогично пункту 3, повторяем шаги для **создания образа datanode**. Единственные различия - другой том data и порт запуска. Dockerfile для datanode приложен в папке.




Итак, мы создали образы base, namenode, datanode и скрипты для запуска. 
**Все необходимые файлы приложены в папке!**



