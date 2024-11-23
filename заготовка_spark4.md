# Apache Spark под управлением YARN

В четвертом практическом домашнем задании наши задачи:

+ Запустить сессию Apache Spark под управлением YARN, развернутого кластера в предыдущих заданиях
+ Подключиться к кластеру HDFS, развернутому в предыдущих заданиях
+ Используя созданную ранее сессию Spark, прочитать данные, которые были предварительно загружены на HDFS
+ Провести несколько трансформаций данных (например, агрегацию или преобразование типов)
+ Сохранить данные как таблицу
+ Убедиться, что стандартный клиент Hive может прочитать данные.
+ **Бонус для повышения оценки:** применить 5 трансформаций разных видов и сохранить данные как партиционированную таблицу.

В рамках учебного курса нам предоставили сервера для выполнения домашнего задания.

Мы разбили задачу на отдельные шаги, которые вы найдете в markdown-файле **spark_with_yarn.md**.


Приятного просмотра!


# Пример работы со Spark под управлением YARN

В этом пошаговом руководстве описано, как запускать и корректно завершать сессию Spark, а также инструкции по выполнению базовых операций с таблицей. (Предполагается, что дистрибутив Spark уже установлен, существуют работающий кластер Hadoop и HDFS, содержащая базу данных). 

## 0. Virtual environment
В этом задании мы используем интерактивную оболочку ipython.

Если у вас еще не установлена виртуальная среда для работы с python, то можно это сделать с помощью этого кода:
```
sudo apt-get install python3-virtualenv
virtualenv -p python3 ~/venv
source venv/bin/activate
pip3 install ipython
```

В дальнейшем можно начинать работу следующим образом: заходим в виртуальную среду, затем запускаем ipython
```
source venv/bin/activate
ipython
```

## 1. Создаем сессию Spark
Чтобы работать со Spark из python используется пакет `pyspark`. Его можно установить командой `pip install pyspark`, но поскольку дистрибутив Spark уже включает в себя этот пакет, то его отдельная установка приведет к скачиванию всего дистрибутива Spark. 

Мы для наших тренировочных целей будем использовать pyspark прямо из дистрибутива Spark. Для этого выполним код:

```
import os, sys

for root, dirs, files in os.walk(f"{os.environ['SPARK_HOME']}/python/lib"):
    for file in files:
        if "zip" in file:
            sys.path.insert(0, os.path.join(root, file))
```

Далее создаем новую сессию Spark:
```
from pyspark.sql import SparkSession
from onetl.connection import SparkHDFS
from onetl.file import FileDFReader
from onetl.file.format import CSV

spark = SparkSession.builder \
    .master("yarn") \
    .appName("spark-with-yarn") \
    .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
    .config("spark.hive.metastore.uris", "thrift://tmpl-dn-01:хххх") \
    .enableHiveSupport() \
    .getOrCreate()

```

**Очень важно не забыть закрыть сессию после рабыты!**

Команда `spark.stop()`

Выход из среды `quit()`

## 2. Подключимся к файловой системе HDFS
```
hdfs = SparkHDFS(host="tmpl-nn", port=9000, spark=spark, cluster="test")
```

Проверим, что успешно:
```
In [4]: hdfs.check()
Out[4]: SparkHDFS(cluster='test', host='tmpl-nn', ipc_port=9000)
```

## 3. Читаем файл
пример:
```
reader = FileDFReader(connection=hdfs, format=CSV(delimiter=",", header=True), source_path="/input")

df = reader.run(["your_file_name.csv"])
```

## 4. Базовый обзор таблицы
Получить количество строк можно командой `df.count()`. Пример:
```
In [7]: df.count()
Out[7]: 999507
```

Получить список колонок, описание типов и информацию о наличии пропусков - `df.printSchema()`. Пример:
```
In [8]: df.printSchema()
root
 |-- registration number: string (nullable = true)
 |-- registration date: string (nullable = true)
 |-- application number: string (nullable = true)
 |-- application date: string (nullable = true)
 |-- priority date: string (nullable = true)
 |-- exhibition priority date: string (nullable = true)
```

Выбрать колонку и посмотреть первые несколько строк (default 20). 
```
dt = df.select("registration date")
dt.show()
```

Пример:
```
In [9]: dt = df.select("registration date")
   ...: dt.show()
+-----------------+
|registration date|
+-----------------+
|         19361027|
|         19361027|
|         19361027|
|         19361027|
```

-----------------------------------

## На примере разберем несколько видов трансформации данных:

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
----------------------------------

## Сохраним данные как таблицу
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
-----------------------------------

## Убедимся, что стандартный клиент Hive может прочитать данные
```
source ~/.profile
```

-----------------------------------

## Бонус
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
Удалить старую таблицу (по желанию):
  ```sql

DROP TABLE test.numbers;
 ```
Переименовать новую таблицу (по желанию):
  ```sql
ALTER TABLE test.numbers_partitioned RENAME TO test.numbers;
 ```
