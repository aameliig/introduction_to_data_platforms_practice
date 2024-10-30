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

![image](https://github.com/aameliig/introduction_to_data_platforms_practice/blob/task3_hive_set_up_guide/pictures/image_2024-10-27_16-17-15.png)


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

## 12. Cоздаем папки
Для хранения данных нам понадобятся папки tmp и warehouse. Cоздадим их командами:
```
hdfs dfs -mkdir -p /tmp
hdfs dfs-mkdir -p /user/hive/warehouse
```
**Совет:** для начала убедитесь, что этих папок не существует. Это можно сделать в веб-интерфейсе, вкладка 
`Utilities / Browse the file system`

В нашем случае папка tmp уже существовала, мы добавили только warehouse.

Меняем права доступа:
```
hdfs dfs -chmod g+w  /tmp
hdfs dfs -chmod g+w  /user/hive/warehouse
```

Вид веб-интерфейса:

![image](https://github.com/aameliig/introduction_to_data_platforms_practice/blob/task3_hive_set_up_guide/pictures/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0_20241026_141316.png)

## 12. Инициализируем БД
Перед запуском осталось инициализировать БД:
```
cd ../
./schematool -dbType postgres -initSchema
```

## 13. Запускаем Hive
```
nohup hive --hiveconf hive.server2.enable.doAs=false --hiveconf hive.security.authorization.enabled=false --service hiveserver2 1>> /tmp/hs2.log 2>> /tmp/hs2.log &
```

Подключиться в консоль Hive можно командой:
```
beeline -u jdbc:hive2://team-1-jn:5432
```

## 14. Проверка: DB test
Чтобы убедиться, что все работает корректно создадим DATABASE test.

```
SHOW DATABASES;
```

![image](https://github.com/aameliig/introduction_to_data_platforms_practice/blob/task3_hive_set_up_guide/pictures/image_2024-10-27_16-12-12.png)

```
CREATE DATABASE test;
DESCRIBE DATABASE test;
```

![image](https://github.com/aameliig/introduction_to_data_platforms_practice/blob/task3_hive_set_up_guide/pictures/image_2024-10-27_16-12-43.png)

БД появилась в веб-интерфейсе:

![image](https://github.com/aameliig/introduction_to_data_platforms_practice/blob/task3_hive_set_up_guide/pictures/photo_2024-10-28_08-19-20.jpg)


## 14.5 Посмотрим веб-интерфейс Hive
Подключиться к нему можно по ссылке: http://176.109.91.3:10002

![image](https://github.com/aameliig/introduction_to_data_platforms_practice/blob/task3_hive_set_up_guide/pictures/photo_2024-10-28_08-19-08.jpg)


## Настройка Hive завершена. Переходим к операциям с данными

------------------------------------


### Шаги работы с HDFS и Hive

1. **Создание директории в HDFS**
   ```bash
   hdfs dfs -mkdir /input
   ```
   - Создает директорию `/input` в файловой системе HDFS, которая будет использоваться для хранения данных.

2. **Изменение прав доступа к директории**
   ```bash
   hdfs dfs -chmod g+w /input
   ```
   - Устанавливает права на запись для группы (`g+w`) в директории `/input`, позволяя другим пользователям в группе добавлять файлы.

3. **Копирование файла в HDFS**
   ```bash
   hdfs dfs -put ./apache-hive-4.0.1-bin/examples/files/2000_cols_data.csv /input/
   ```
   - Копирует файл `2000_cols_data.csv` из локальной файловой системы в директорию `/input` в HDFS.

4. **Проверка целостности файла**
   ```bash
   hdfs fsck /input/2000_cols_data.csv
   ```
   - Выполняет проверку целостности файла `2000_cols_data.csv` в HDFS, чтобы убедиться, что файл доступен и не поврежден.

5. **Подключение к Hive через Beeline**
   ```bash
   beeline -u jdbc:hive2://team-1-jn:5432
   ```
   - Подключается к Hive через Beeline, используя JDBC URL, чтобы взаимодействовать с базой данных.

6. **Просмотр доступных баз данных**
   ```sql
   SHOW DATABASES;
   ```
   - Отображает список всех баз данных в Hive, чтобы убедиться, что нужная база данных доступна.

7. **Выбор базы данных**
   ```sql
   use test;
   ```
   - Выбирает базу данных `test` для дальнейших операций.

8. **Создание таблицы**
   ```sql
   CREATE TABLE IF NOT EXISTS test.numbers (
       num1 STRING,
       num2 STRING,
       num3 STRING,
       num4 STRING
   ) 
   ROW FORMAT DELIMITED 
   FIELDS TERMINATED BY ',';
   ```
   - Создает таблицу `numbers` в базе данных `test`, если она еще не существует. Таблица имеет четыре столбца, все из которых имеют тип `STRING`. Данные будут разделены запятыми.

9. **Просмотр таблиц в базе данных**
   ```sql
   SHOW TABLES;
   ```
   - Отображает список всех таблиц в текущей базе данных, чтобы проверить, была ли успешно создана таблица `numbers`.

10. **Описание структуры таблицы**
    ```sql
    DESCRIBE numbers;
    ```
    - Показывает структуру таблицы `numbers`, включая названия столбцов и их типы данных.

11. **Загрузка данных в таблицу**
    ```sql
    LOAD DATA INPATH '/input/decimal64table1.csv' INTO TABLE test.numbers;
    ```
    - Загружает данные из файла `decimal64table1.csv`, который находится в HDFS, в таблицу `numbers`.

12. **Запрос данных из таблицы**
    ```sql
    SELECT * FROM test.numbers LIMIT 10;
    ```
    - Выполняет запрос для получения первых 10 записей из таблицы `numbers`, позволяя проверить, что данные были успешно загружены.
13. **Работа с партициями**
    
По порядку: 
Создать новую партиционированную таблицу:

  ```sql
CREATE TABLE IF NOT EXISTS test.numbers_partitioned (
    num2 STRING,
    num3 STRING,
    num4 STRING
)
PARTITIONED BY (num1 STRING)  -- Указать столбец для партиционирования
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY ',';
  ```
Перенести данные из старой таблицы в новую таблицу:
  ```sql

INSERT INTO TABLE test.numbers_partitioned PARTITION (num1)
SELECT num1, num2, num3, num4 FROM test.numbers;
  ```
Проверить наличие партиций:

  ```sql
SHOW PARTITIONS test.numbers_partitioned;
  ```
Консоль:

![image](https://github.com/aameliig/introduction_to_data_platforms_practice/blob/task3_hive_set_up_guide/pictures/photo_2024-10-30_08-11-11.jpg)

Веб-интерфейс:

![image](https://github.com/aameliig/introduction_to_data_platforms_practice/blob/task3_hive_set_up_guide/pictures/part.jpg)

Удалить старую таблицу (по желанию):
  ```sql

DROP TABLE test.numbers;
 ```
Переименовать новую таблицу (по желанию):
  ```sql
ALTER TABLE test.numbers_partitioned RENAME TO test.numbers;
 ```
