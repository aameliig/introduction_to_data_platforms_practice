# Hive Installation Guide

В третьем практическом домашнем задании наша цель:

+ развернуть **Hive** в конфигурации пригодной для производственной эксплуатации (с отдельным хранилищем метаданных)
+ трансформировать загруженные данные в таблицу Hive
+ преобразовать полученную таблицу в партиционированную
+ подробно описать этот процесс

В рамках учебного курса нам предоставили сервера для выполнения домашнего задания: одна Jump Node, одна Name Node, две Data Node.

Мы разбили задачу на отдельные шаги, которые вы найдете в markdown-файле **hive_instruction.md**.


Приятного просмотра!



# Подробная инструкция по настройке Hive

Следуя этому пошаговому руководству, вы сможете развернуть свой развернуть **Hive** в конфигурации пригодной для производственной эксплуатации (с отдельным хранилищем метаданных), а также трансформировать загруженные данные в таблицу Hive и преобразовать полученную таблицу в партиционированную.

## 1. Установим postgresql
Для начала переключимся в Name Node и установим postgresql. С его помощью будет организовано хранилище метаданных

```
ssh team-1-nn
sudo apt install postgresql
```

Переключимся в **пользователя postgres**

```
sudo -i -u postgres
```

## 2. Создаем базу для метаданных
Откроем консоль postgresql командой `psql`

```
CREATE DATABASE metastore;
```
Далее создаем нового пользователя hive и даем ему права доступа. Но этого не достаточно: нужно также назначить его владельцем БД.
```
CREATE USER hive with password '<your_password>';

GRANT ALL PRIVILEGES ON DATABASE "metastore" TO hive;

ALTER DATABASE metastore OWNER TO hive;
```

## 3. Редактируем конфигурационные файлы
Выходим в пользователя team на name node; открываем конфигурационные файлы и правим следующие строки:
```
sudo nano /etc/postgresql/16/main/postgresql.conf
```
```
listen_addresses = 'team-1-nn'
```
Второй конфиг:
```
sudo nano /etc/postgresql/16/main/pg_hba.conf
```
```
host    metastore       hive            192.168.1.6/32          password 

        # наша бд       #пользователь   # адрес jump node      #способ авторизации
```

## 4. Рестартуем postgresql, чтобы применить изменения
```
sudo systemctl restart postgresql
```

Можно проверить себя командой `sudo systemctl status postgresql`

## 5. Установим клиент postgresql на jump node
Возвращаемся на jump node, установим клиент postgresql
```
sudo apt install postgresql-client-16
```

Можно проверить себя: пробуем подключиться к metastore - работает!
```
psql -h team-1-nn -p 5432 -U hive -W -d metastore
```

## 6. Скачиваем диструбитив Hive
Для начала переключимся в пользователя hadoop:

```
su hadoop
```

Скачиваем Hive (version = 4.0.1):

```
wget https://dlcdn.apache.org/hive/hive-4.0.1/apache-hive-4.0.1-bin.tar.gz
```

## 7. Распаковываем архив
```
tar -zxvf apache-hive-4.0.1-bin.tar.gz
cd apache-hive-4.0.1-bin/
```

## 8. Скачиваем драйвер для postgresql
```
cd libs
wget https://jdbc.postgresql.org/download/postgresql-42.7.4.jar
```

## 9. Конфигурирование
Создадим свой конфигурационный файл
```
cd ../conf
nano hive-site.xml
```

**Содержимое hive-site.xml**
```                                  
<configuration>
  <property>
    <name>hive.server2.authentication</name>
    <value>NONE</value>
  </property>
  <property>
    <name>hive.metastore.warehouse.dir</name>
    <value>/user/hive/warehouse</value>
  </property>
  <property>    
    <name>hive.server2.thrift.port</name>
    <value>5433</value>
  </property>
  <property>    
    <name>javax.jdo.option.ConnectionURL</name>
    <value>jdbc:postgresql://team-1-nn:5432/metastore</value>
  </property>
  <property>    
    <name>javax.jdo.option.ConnectionDriverName</name>
    <value>org.postgresql.Driver</value>
  </property>
  <property>    
    <name>javax.jdo.option.ConnectionUserName</name>
    <value>hive</value>
  </property>
  <property>    
    <name>javax.jdo.option.ConnectionPassword</name>
    <value>your_password</value>
  </property>   
</configuration>
```

## 10. Добавим переменные окружения
```
nano ~/.profile
```
Вставляем в конец:
```
export HIVE_HOME="/home/hadoop/apache-hive-4.0.1-bin"
export HIVE_CONF_DIR=$HIVE_HOME/conf
export HIVE_AUX_JARS_PATH=$HIVE_HOME/lib/*
export PATH="$PATH:$HIVE_HOME/bin" 
```

## 11. Активируем окружение
```
source ~/.profile
```

Можно проверить себя командой `hive --version`

----------------------------------

создаем папки 
убедиться что нет
идем в браузер

у нас есть тмп
нужна только одна +1 папка



## 12. Проверяем версию Java и Python
Проверяем, что установлены нужные версии Java и Python. Хотим видеть у себя openjdk version "11.0.24" 
Если их нет, устанавливаем:
```
sudo apt install openjdk-11-jdk python3
```
Смотрим, где живет Java:
```
which java
```
Предыдущий путь вставляем вместо /usr/bin/java далее
```
readlink -f /usr/bin/java
```
## 13. Создаем переменные окружения
Настраиваем переменные окружения для Hadoop и Java, добавляем пути в `.profile`:
```
nano ~/.profile
```
следующие пути:
```
export HADOOP_HOME=/home/hadoop/hadoop-3.4.0
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
```

Применяем изменения:

```
source ~/.profile
```
И проверяем, что всё рабоает:
```
hadoop version
```
Должна вывестись версия Hadoop, пока мы находимся в домашней директории.

## 14. Копируем файл на все ноды
Переносим файл окружения на остальные ноды, кроме jump ноды:

```
scp ~/.profile team-1-dn-0:/home/hadoop/
scp ~/.profile team-1-dn-1:/home/hadoop/
```

## 14.5 Добавляем на всякий случай путь к Java в конфиг Hadoop напрямую:
```
cd hadoop-3.4.0/etc/hadoop/
nano hadoop-env.sh
```
и добавляем строчку:
```
JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
```
и аналогично копируем на остальные ноды, кроме jump-ноды:
```
scp hadoop-env.sh team-1-dn-0:/home/hadoop/hadoop-3.4.0/etc/hadoop/hadoop-env.sh
scp hadoop-env.sh team-1-dn-1:/home/hadoop/hadoop-3.4.0/etc/hadoop/hadoop-env.sh
```

## 15. Редактируем конфигурацию core-site.xml
Открываем и редактируем файл `core-site.xml`:

```
nano /home/hadoop/hadoop-3.4.0/etc/hadoop/core-site.xml
```

Добавляем:

```
<property>
  <name>fs.defaultFS</name>
  <value>hdfs://team-1-nn:9000</value>
</property>
```

## 16. Редактируем hdfs-site.xml
Настраиваем HDFS и указываем репликацию:

```
nano /home/hadoop/hadoop-3.4.0/etc/hadoop/hdfs-site.xml
```

Добавляем:

```
<property>
  <name>dfs.replication</name>
  <value>3</value>
</property>
```

## 17. Редактируем файл workers
Добавляем ноды в файл `workers`:

```
nano /home/hadoop/hadoop-3.4.0/etc/hadoop/workers
```

Пример:

```
team-1-nn
team-1-dn-0
team-1-dn-1
```

## 18. Копируем конфиги на все ноды
Переносим конфиги на другие ноды:

```
scp core-site.xml team-1-dn-0:/home/hadoop/hadoop-3.4.0/etc/hadoop/core-site.xml
scp core-site.xml team-1-dn-1:/home/hadoop/hadoop-3.4.0/etc/hadoop/core-site.xml

scp hdfs-site.xml team-1-dn-0:/home/hadoop/hadoop-3.4.0/etc/hadoop/hdfs-site.xml
scp hdfs-site.xml team-1-dn-1:/home/hadoop/hadoop-3.4.0/etc/hadoop/hdfs-site.xml

scp workers team-1-dn-0:/home/hadoop/hadoop-3.4.0/etc/hadoop/workers
scp workers team-1-dn-1:/home/hadoop/hadoop-3.4.0/etc/hadoop/workers
```

## 19. Запускаем HDFS
Форматируем файловую систему и запускаем HDFS:
из hadoop-3.4.0 запускаем
```
bin/hdfs namenode -format
sbin/start-dfs.sh
```

## 20. Переходим на джамп-ноду
Подключаемся к джамп-ноду для настройки nginx:

```
ssh hadoop@jumpnode
```

## 21. Меняем конфиг nginx
Переходим обратно в пользователя team
Редактируем конфигурацию nginx:

```
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/nn
sudo nano /etc/nginx/sites-available/nn
```

Добавляем правила для перенаправления трафика на NameNode:

```
server {
  listen 9870;
  location / {
    proxy_pass http://team-1-nn:9870;
  }
}
```
sudo ln -s /etc/nginx/sites-available/nn /etc/nginx/sites-enabled/nn

## 22. Перезагружаем nginx
Применяем изменения:

```
sudo systemctl restart nginx
```

## 23. Проверяем доступность через браузер
Переходим в браузере по адресу джамп-ноды и проверяем доступность Hadoop NameNode.
http://176.109.91.3:9870
Смотрим, что все работает и все три ноды живые
![image](https://github.com/user-attachments/assets/f6715df3-b66a-453a-bb9d-411ecce2dc48)
![image](https://github.com/user-attachments/assets/f33a03cb-6a3d-41ac-9e1d-e47df4aa1141)



## 24. Заходим на нейм-ноду
Переходим в пользователя hadoop:
sudo -i -u hadoop
Подключаемся обратно на NameNode:

```
ssh team-1-nn
```

## 25. Настраиваем конфиги YARN

cd hadoop-3.4.0/etc/hadoop

Открываем и редактируем `yarn-site.xml` и `mapred-site.xml`:

nano yarn-site.xml

```
<property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.env-whitelist</name>
<value>JAVA_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR,CLASSPATH_PREPEND_DISTCACHE,HADOOP_YARN_HOME,HADOOP_HOME,PATH,LANG,TZ,HADOOP_MAPRED_HOME</value>    </property>

```

nano mapred-site.xml

```
<configuration>
   <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
   </property>
   <property>
        <name>mapreduce.application.classpath</name>
        <value>$HADOOP_HOME/share/hadoop/mapreduce/*:$HADOOP_HOME/share/hadoop/mapreduce/lib/*</value>
   </property>
</configuration>
```

## 26. Копируем конфиги на остальные ноды
Переносим конфиги YARN на другие ноды:

```
scp mapred-site.xml team-1-dn-0:/home/hadoop/hadoop-3.4.0/etc/hadoop
scp mapred-site.xml team-1-dn-1:/home/hadoop/hadoop-3.4.0/etc/hadoop
scp yarn-site.xml team-1-dn-0:/home/hadoop/hadoop-3.4.0/etc/hadoop
scp yarn-site.xml team-1-dn-1:/home/hadoop/hadoop-3.4.0/etc/hadoop
```

## 27. Запускаем YARN
cd ../../
Запускаем сервисы YARN:

```
sbin/start-yarn.sh
```

## 28. Запускаем History Server
Запускаем сервер истории:

```
mapred --daemon start historyserver
```

## 29. Редактируем конфиги для веб-интерфейсов
Настраиваем порты для веб-интерфейсов YARN и History Server:

Выходим из nn на jn, и переходим в пользователя team

```
exit
su team
```
Редактируем конфиг
```
sudo cp /etc/nginx/sites-available/nn /etc/nginx/sites-available/ya
sudo cp /etc/nginx/sites-available/nn /etc/nginx/sites-available/dh

sudo nano /etc/nginx/sites-available/ya
```
server {
  listen 8088;
  location / {
    proxy_pass http://team-1-nn:8088;
  }
}

sudo nano /etc/nginx/sites-available/dh

server {
  listen 19888;
  location / {
    proxy_pass http://team-1-nn:19888;
  }
}

Включаем хосты:
sudo ln -s /etc/nginx/sitest-available/ya /etc/nginx/sites-enabled/ya
sudo ln -s /etc/nginx/sitest-available/dh /etc/nginx/sites-enabled/dh


## 30. Перезапускаем nginx
Перезагружаем nginx после изменения конфигурации:

```
sudo systemctl restart nginx
```

