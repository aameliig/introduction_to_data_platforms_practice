# Hadoop Installation Guide

В первом и втором практических домашних заданиях наша цель:
+ развернуть кластер Hadoop, состоящий из:
    - одной **Jump Node**
    - одной **Name Node**
    - двух **Data Node**

+ запустить **YARN**
+ сделать обзор веб-интерфейсов
+ подробно описать этот процесс

В рамках учебного курса нам предоставили сервера для запуска каждой ноды.

Мы разбили задачу на отдельные шаги, которые вы найдете в markdown-файле **main_hadoop_instruction.md**.

------------

Также, мы предлагаем **бонусное решение**, которое подразумевает развертывание кластеров Hadoop на одном устройстве, используя Docker.
Это может быть полезно в качестве самостоятельной практики и для того, чтобы познакомиться с системой Hadoop при отсутствии доступа к сторонним серверам.

Вот его план:

0. Анализ структуры, составление плана действий 
1. Подготовка образов base, namenode, datanode
2. Создание конфигурационных файлов в config.dir
3. Запуск hadoop + команда остановки
4. Проверка статуса кластера

Каждый этап и материалы к нему - в соответствующих папках, пометка **bonus_docker**.


Приятного просмотра!



# Подробная инструкция по настройке Hadoop-кластера

Следуя этому пошаговому руководству, вы сможете развернуть свой Hadoop-кластер. 
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
![create new user](https://github.com/aameliig/introduction_to_data_platforms_practice/blob/test/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0_20241011_152536-1.png)


## 3. Добавляем в список хостов пути к остальным нодам
Для того, чтобы ноды знали друг про друга, редактируем файл `/etc/hosts`. Добавляем туда IP-адресов всех узлов и закомментируем лишние:

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
Эта операция доступна только для пользователя с правом sudo (не hadoop). 

## 4. Генерируем SSH-ключи
Переключаемся в **пользователя hadoop**:

```
su hadoop
```

Для доступа без пароля создаём SSH-ключи (важно: генерируем ключи из под **hadoop**!):

```
ssh-keygen
```

Выведем в консоль публичный ключ и **скопируем его себе в отдельный текстовый файл**:

```
cat ./ssh/id_ed255219.pub
```
Затем выходим из пользователя hadoop и подключаемся к другой ноде.

## 5. Повторяем шаги 2 - 4 на всех узлах
Повторяем предыдущие шаги 2 - 4 (создание пользователя, корректировка списка хостов и генерация ключей) на всех остальных нодах.
К ним мы подключаемся через jump node

## 6. Создаем файл с SSH-ключами
Идем на Jump Node и переключаемся в пользователя hadoop. Заходим в папку ./ssh и создаем там файл authorized_keys:

```
nano authorized_keys
```

Туда мы вставляем публичные SSH-ключи от всех нод, которые мы заранее для удобства сохранили в отдельном текстовом файлике.

## 7. Кладем ключи на остальные ноды
Далее копируем ключи (этот файл) на все остальные узлы командой:
```
scp authorized_keys team-1-nn:/home/hadoop/.ssh/
```

После этого шага можно проверить, что подключение по SSH к другим нодам происходит успешно (то есть, от нас не требуется вводить пароль):
```
ssh <node_name>

пример:
ssh team-1-nn
```
После этой команды вы должны зайти на хост без ввода пароля.

## 8. Устанавливаем Hadoop на Jump Node
Возвращаемся на Jump Node, переключаемся в hadoop. Скачиваем Hadoop, у нас версия 3.4.0:

```
wget https://downloads.apache.org/hadoop/common/hadoop-3.4.0/hadoop-3.4.0.tar.gz
```

## 9. Копируем дистрибутив Hadoop на все узлы
Перемещаем архив с Hadoop на все ноды:

```
scp hadoop-3.4.0.tar.gz <node_name>:/home/hadoop/

пример:
scp hadoop-3.4.0.tar.gz team-1-nn:/home/hadoop/
```

## 10. Распаковываем Hadoop на всех нодах
Распаковываем архив на каждой ноде:

```
tar -xzvf hadoop-3.4.0.tar.gz
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
