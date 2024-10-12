# Hadoop Installation Guide

В первом практическом задании наша цель - развернуть кластер Hadoop и подробно описать этот процесс.
Кластер должен содержать **1 NameNode** и **3 DataNode**. Каждая Node представляет из себя отдельно работающий host (узел).
В рамках учебного курса нам предоставили сервера для запуска каждой ноды.


Мы разбили задачу на этапы:

1. Предусловия (java, пользователь, ssh) (Амелия Алаева)
2. Установка (Николас Евкарпиди)
3. Конфигурирование (Николас Евкарпиди)
4. Запуск (проверка статуса кластера, обзор веб-интерфейсов namenode и datanode) (Юрий Маркелов)


Каждый этап и материалы к нему - в соответствующих папках.


Также, мы предлагаем **бонусное решение**, которое подразумевает развертывание кластеров Hadoop на одном устройстве, используя Docker.
Это может быть полезно в качестве самостоятельной практики и для того, чтобы познакомиться с системой Hadoop при отсутствии доступа к сторонним серверам.

Решение разработала Амелия Алаева. Вот его план:

0. Анализ структуры, составление плана действий 
1. Подготовка образов base, namenode, datanode
2. Создание конфигурационных файлов в config.dir
3. Запуск hadoop + команда остановки
4. Проверка статуса кластера

Каждый этап и материалы к нему - в соответствующих папках, пометка **bonus_docker**.


Приятного просмотра!



# Подробная инструкция по настройке Hadoop-кластера

Следуя этому пошаговому руководству, вы сможете развернуть Hadoop-кластер. 
Мы показываем пример для 4-х нод: одна **Jump Node**, одна **Name Node**, две **Data Node**; 
Однако можно, например, подключить большее число Data Nodes, но основная логика настройки останется такой же.

## 1. Подключаемся к серверам
Для начала убедитесь, что вы располагаете ресурсами - серверами, так как каждая нода (узел) - это отдельный хост.

Используем SSH для подключения к Jump Node, так как она доступна из внешней сети:

```
ssh team@<IP-адрес>
```

Взаимодействие с другими узлами будет происходить через нее.

## 2. Создаем пользователя hadoop
Создаем нового пользователя для работы с Hadoop (без прав sudo) и придумываем ему надежный пароль:

```
sudo adduser hadoop
```
![create new user](http://url/to/img.png)

Переключаемся в пользователя hadoop:

```
su hadoop
```

## 3. Генерируем SSH-ключи
Для доступа без пароля создаём SSH-ключи:

```
ssh-keygen -t rsa -P ""
```
Скопируем публичный ключ id_rsa.pub
Затем добавляем ключ в авторизованные:

```
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
```

## 4. Меняем в списке хостов пути к остальным нодам
Редактируем файл `/etc/hosts` для добавления IP-адресов всех нод:

```
sudo nano /etc/hosts
```

Пример записи:

```
192.168.1.6 team-1-jn
192.168.1.7 team-1-nn
192.168.1.8 team-1-dn-0
192.168.1.9 team-1-dn-1

```

!!!!!!
## 5. Повторяем шаги 2, 4 на всех узлах
Повторяем предыдущие шаги (создание пользователя,  ключей, настройка хостов) на всех остальных нодах.
Подключаемся через jump node

```
eam@team-1-nn:~$ sudo nano /etc/hosts
team@team-1-nn:~$ su hadoop
Password: 
hadoop@team-1-nn:/home/team$ cd ~
hadoop@team-1-nn:~$ cd .ssh
bash: cd: .ssh: No such file or directory
hadoop@team-1-nn:~$ mkdir .ssh
hadoop@team-1-nn:~$ cd .ssh
hadoop@team-1-nn:~/.ssh$ nano master.pub
hadoop@team-1-nn:~/.ssh$ cat ~/.ssh/master.pub >> ~/.ssh/authorized_keys
hadoop@team-1-nn:~/.ssh$ 

```
hadoop@team-1-dn-01:~/.ssh$ nano master.pub
hadoop@team-1-dn-01:~/.ssh$ cat ~/.ssh/master.pub >> ~/.ssh/authorized_keys


## 6. Устанавливаем Hadoop на джамп-ноду
Скачиваем Hadoop и устанавливаем его на джамп-ноду:

```
wget https://downloads.apache.org/hadoop/common/hadoop-3.4.0/hadoop-3.4.0.tar.gz
tar -xzvf hadoop-3.4.0.tar.gz
```

## 7. Создаем файл с ключами
Сохраняем SSH-ключи в отдельный файл для последующей отправки:

```
ssh-keygen -t rsa -P "" -f ~/.ssh/hadoop_key
```

## 8. Раскладываем ключи на остальные ноды
Копируем ключи на все остальные ноды:

```
ssh-copy-id -i ~/.ssh/hadoop_key.pub user@node1
ssh-copy-id -i ~/.ssh/hadoop_key.pub user@node2
```

## 9. Копируем дистрибутив Hadoop на ноды
Перемещаем архив с Hadoop на все ноды:

```
scp hadoop-3.3.0.tar.gz user@node1:/home/hadoop/
scp hadoop-3.3.0.tar.gz user@node2:/home/hadoop/
```

## 10. Распаковываем Hadoop на всех нодах
Распаковываем архив с Hadoop на каждой ноде:

```
tar -xzvf hadoop-3.3.0.tar.gz
```

## 11. Переходим на нейм-нод
Подключаемся к NameNode:

```
ssh hadoop@node1
```

## 12. Проверяем версию Java и Python
Проверяем, что установлены нужные версии Java и Python. Если их нет, устанавливаем:

```
sudo apt install openjdk-8-jdk python3
```

## 13. Создаем переменные окружения
Настраиваем переменные окружения для Hadoop и Java, добавляем пути в `.bashrc`:

```
export HADOOP_HOME=/home/hadoop/hadoop-3.3.0
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$PATH:$HADOOP_HOME/bin
```

Применяем изменения:

```
source ~/.bashrc
```

## 14. Копируем файл на все ноды
Переносим файл окружения на остальные ноды:

```
scp ~/.bashrc user@node2:/home/hadoop/
scp ~/.bashrc user@node3:/home/hadoop/
```

## 15. Редактируем конфигурацию core-site.xml
Открываем и редактируем файл `core-site.xml`:

```
nano $HADOOP_HOME/etc/hadoop/core-site.xml
```

Добавляем:

```
<property>
  <name>fs.defaultFS</name>
  <value>hdfs://node1:9000</value>
</property>
```

## 16. Редактируем hdfs-site.xml
Настраиваем HDFS и указываем репликацию:

```
nano $HADOOP_HOME/etc/hadoop/hdfs-site.xml
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
nano $HADOOP_HOME/etc/hadoop/workers
```

Пример:

```
node1
node2
node3
```

## 18. Копируем конфиги на все ноды
Переносим конфиги на другие ноды:

```
scp $HADOOP_HOME/etc/hadoop/* user@node2:/home/hadoop/hadoop-3.3.0/etc/hadoop/
```

## 19. Запускаем HDFS
Форматируем файловую систему и запускаем HDFS:

```
$HADOOP_HOME/bin/hdfs namenode -format
$HADOOP_HOME/sbin/start-dfs.sh
```

## 20. Переходим на джамп-ноду
Подключаемся к джамп-ноду для настройки nginx:

```
ssh hadoop@jumpnode
```

## 21. Меняем конфиг nginx
Редактируем конфигурацию nginx:

```
nano /etc/nginx/nginx.conf
```

Добавляем правила для перенаправления трафика на NameNode:

```
server {
  listen 80;
  location / {
    proxy_pass http://node1:9870;
  }
}
```

## 22. Перезагружаем nginx
Применяем изменения:

```
sudo systemctl restart nginx
```

## 23. Проверяем доступность через браузер
Переходим в браузере по адресу джамп-ноды и проверяем доступность Hadoop NameNode.

## 24. Заходим на нейм-ноду
Подключаемся обратно на NameNode:

```
ssh hadoop@node1
```

## 25. Настраиваем конфиги YARN
Открываем и редактируем `yarn-site.xml` и `mapred-site.xml`:

```
nano $HADOOP_HOME/etc/hadoop/yarn-site.xml
```

Пример настройки:

```
<property>
  <name>yarn.resourcemanager.hostname</name>
  <value>node1</value>
</property>
```

## 26. Копируем конфиги на остальные ноды
Переносим конфиги YARN на другие ноды:

```
scp $HADOOP_HOME/etc/hadoop/* user@node2:/home/hadoop/hadoop-3.3.0/etc/hadoop/
```

## 27. Запускаем YARN
Запускаем сервисы YARN:

```
$HADOOP_HOME/sbin/start-yarn.sh
```

## 28. Запускаем History Server
Запускаем сервер истории:

```
$HADOOP_HOME/bin/mapred --daemon start historyserver
```

## 29. Редактируем конфиги для веб-интерфейсов
Настраиваем порты для веб-интерфейсов YARN и History Server:

```
nano $HADOOP_HOME/etc/hadoop/yarn-site.xml
```

Пример:

```
<property>
  <name>yarn.resourcemanager.webapp.address</name>
  <value>node1:8088</value>
</property>
```

## 30. Перезапускаем nginx
Перезагружаем nginx после изменения конфигурации:

```
sudo systemctl restart nginx
```

## 31. Останавливаем сервисы
Для завершения, останавливаем все сервисы:

```
$HADOOP_HOME/sbin/stop-yarn.sh
$HADOOP_HOME/sbin/stop-dfs.sh
$HADOOP_HOME/bin/mapred --daemon stop historyserver
```

Теперь кластер настроен и готов к работе!
