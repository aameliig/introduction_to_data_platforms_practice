# Подробная инструкция по настройке Hadoop-кластера

Следуя этому пошаговому руководству, вы сможете развернуть свой Hadoop-кластер, который будет состоять из 4-х нод: одна **Jump Node**, одна **Name Node**, две **Data Node**. Нам по SSH доступна только Jump Node.
Однако можно, например, подключить большее число Data Nodes, но основная логика настройки останется такой же.

## 1. Подключаемся к серверам
Для начала убедитесь, что вы располагаете ресурсами - серверами, так как каждая нода (узел) - это отдельный хост.

Используем SSH для подключения к Jump Node, так как только она доступна из внешней сети:

```
ssh username@<IP-адрес>
```

Взаимодействие с другими узлами будет происходить через нее.

## 2. Создаем пользователя hadoop
Создаем нового пользователя для работы с Hadoop (без прав sudo) и придумываем ему надежный пароль:

```
sudo adduser hadoop
```
![create new user](https://github.com/aameliig/introduction_to_data_platforms_practice/blob/test/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0_20241011_152536-1.png)


## 3. Добавляем в список хостов адреса остальных нод
Для того, чтобы обращаться к ноде по ее имени отредактируем файл `/etc/hosts`. Добавляем туда IP-адреса всех узлов и закомментируем лишние:

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
К ним мы подключаемся из консоли Jump Node.

## 6. Создаем файл с SSH-ключами
Идем на Jump Node и переключаемся в пользователя hadoop. Заходим в папку ./ssh и создаем там файл authorized_keys:

```
nano authorized_keys
```

Туда мы вставляем публичные SSH-ключи от всех нод, которые мы заранее для удобства сохранили в отдельном текстовом файлике.

## 7. Копируем ключи на остальные ноды
Копируем публичные ключи (файл authorized_keys) на все остальные узлы командой:
```
scp authorized_keys team-1-nn:/home/hadoop/.ssh/
```

После этого шага можно проверить, что подключение по SSH к другим нодам происходит успешно:
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
```
scp hadoop-3.4.0.tar.gz <node_name>:/home/hadoop/

пример:
scp hadoop-3.4.0.tar.gz team-1-nn:/home/hadoop/
```

## 10. Распаковываем архив Hadoop на каждой ноде
```
tar -xzvf hadoop-3.4.0.tar.gz
```

## 11. Переходим на нейм-нод
Подключаемся к NameNode:

```
ssh hadoop@node1
```

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
```
sudo ln -s /etc/nginx/sites-available/nn /etc/nginx/sites-enabled/nn
```

## 22. Перезагружаем nginx
Применяем изменения:

```
sudo systemctl restart nginx
```

## 23. Проверяем доступность через браузер
Переходим в браузере по адресу джамп-ноды и проверяем доступность Hadoop NameNode.

http://176.109.91.3:9870

Смотрим, что все работает и все три ноды живые. 

![image](https://github.com/user-attachments/assets/f6715df3-b66a-453a-bb9d-411ecce2dc48)
![image](https://github.com/user-attachments/assets/f33a03cb-6a3d-41ac-9e1d-e47df4aa1141)

**Краткий обзор веб-интерфейса:**
Из основных параметров мы можем видеть:
- статус кластера (active)
- время запуска
- версию
- id кластера
- количество работающих нод (Live Nodes)


## 24. Заходим на нейм-ноду
Переходим в пользователя hadoop:
```
sudo -i -u hadoop
```

Подключаемся обратно на NameNode:

```
ssh team-1-nn
```

## 25. Настраиваем конфиги YARN
```
cd hadoop-3.4.0/etc/hadoop
```
Открываем и редактируем `yarn-site.xml` и `mapred-site.xml`:

```
nano yarn-site.xml
```

```
<property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.env-whitelist</name>
<value>JAVA_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR,CLASSPATH_PREPEND_DISTCACHE,HADOOP_YARN_HOME,HADOOP_HOME,PATH,LANG,TZ,HADOOP_MAPRED_HOME</value>    </property>

```

Далее:
```
nano mapred-site.xml
```

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

```
cd ../../
```

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
```

Включаем хосты:
```
sudo ln -s /etc/nginx/sites-available/ya /etc/nginx/sites-enabled/ya
sudo ln -s /etc/nginx/sites-available/dh /etc/nginx/sites-enabled/dh
```

## 30. Перезапускаем nginx
Перезагружаем nginx после изменения конфигурации:

```
sudo systemctl restart nginx
```

Мы можем увидеть веб-интерфейс history server

![history server](https://github.com/aameliig/introduction_to_data_platforms_practice/blob/test/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0_20241011_152536-1.png)