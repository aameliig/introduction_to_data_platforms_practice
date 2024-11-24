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

В этом пошаговом руководстве описано, как запускать и корректно завершать сессию Spark, а также инструкции по выполнению базовых операций с таблицей. (Предполагается, что дистрибутив Spark уже установлен, существуют работающий кластер Hadoop и Hive). 

## 0. Virtual environment
Мы будем использовать интерактивную оболочку ipython.

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

Мы для наших целей будем использовать pyspark прямо из дистрибутива Spark. Для этого выполним код:

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
...
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
...
```

-----------------------------------

## На примере разберем несколько видов трансформаций данных:
В нашей таблице записаны данные о регистрации торговых марок в строковом формате.

## 1. Отделим год от registration date и запишем его в новую колонку reg_year
```
df = df.withColumn("reg_year", F.col("registration date").substr(0, 4))
```

After:
```
In [24]: dt = df.select("reg_year")

In [25]: dt.show()
+--------+
|reg_year|
+--------+
|    1936|
|    1936|
|    1936|
|    1936|
|    1937|
```

## 2. Заполним NaN в correspondence address
```
df = df.na.fill({"correspondence address": "unknown"})
```

Before:
```
In [9]: dt.show()
+----------------------+
|correspondence address|
+----------------------+
|                  NULL|
|  "ООО ""Юридическа...|
|  Бейкер и Макензи ...|
|                  NULL|
```

After:
```
n [26]: dt = df.select("correspondence address")

In [27]: dt.show()
+----------------------+
|correspondence address|
+----------------------+
|               unknown|
|  "ООО ""Юридическа...|
|  Бейкер и Макензи ...|
|               unknown|
|               unknown|
```

## 3. Создадим колонку sound_filled из sound: заменим false и Null -> "Нет"

```
df = df.withColumn(
    'sound_filled',
    F.when((F.col("sound") == 'false') | (F.col("sound").isNull()), "Нет")
    .otherwise(F.col("sound"))
)
```
Before:
```
In [17]: dt.show()
+--------------------+
|               sound|
+--------------------+
|               false|
|                NULL|
|               false|
|               false|
|               false|
|               false|
|               false|
|                NULL|
|               false|
|               false|
|               false|
|"Все словесные об...|
|               false|
```

After:
```
In [23]: dt.show()
+--------------------+
|        sound_filled|
+--------------------+
|                 Нет|
|                 Нет|
|                 Нет|
|                 Нет|
|                 Нет|
|                 Нет|
|                 Нет|
|                 Нет|
|                 Нет|
|                 Нет|
|                 Нет|
|"Все словесные об...|
|                 Нет|
```


----------------------------------

## Сохраним данные как таблицу
```
df.write.saveAsTable("your_table_name")
```

## Сохраним данные как партиционированную таблицу
Посмотрим на текущее количество партиций:
```
In [28]: df.rdd.getNumPartitions()
Out[28]: 5
```
Допустим, мы хотим изменить их количество и сохранить партиционированную таблицу. Логично будет разделить данные, например, по году:
```
df.write.parquet("your_table_name")
df = df.repartition(15, "reg_year")
df.rdd.getNumPartitions()
df.write.saveAsTable("your_table_name")
```
-----------------------------------

## Убедимся, что стандартный клиент Hive может прочитать данные

## 1. Подключимся в консоль Hive 
```
beeline -u jdbc:hive2://xxx-xx-xx:port
```

## 2. Проверяем наличие таблиц
```
SHOW DATABASES;

+----------------+
| database_name  |
+----------------+
| default        |
+----------------+

use default;

SHOW TABLES;

+----------------------------+
|          tab_name          |
+----------------------------+
| avg_year_country_20241124  |
| count_country_20241124     |
| max_year_country_20241124  |
| min_year_country_20241124  |
| regs_20241124              |
+----------------------------+

```

Видим таблицы, которые мы создали.

Можем посмотреть на описание одной из них:
```
DESCRIBE count_country_20241124;

+----------------------------+------------+----------+
|          col_name          | data_type  | comment  |
+----------------------------+------------+----------+
| right holder country code  | string     |          |
| count                      | bigint     |          |
+----------------------------+------------+----------+
```

-----------------------------------

## Бонус
Разберем чуть более сложные операции аггрегирования на примере наших данных.

## 1. Поменяем формат колонки на числовой
Это нам понадобится для дальнейших аггрегаций. 
```
df = df.withColumn("int_reg_year",  df.reg_year.cast('integer'))
```

Получили год регистрации торговой марки в целочисленном представлении

## 2. Посчитаем количество right holder country code 
```
table1 = df.groupBy("right holder country code")
table1.show()
table1.write.saveAsTable("count_country_20241124")
```
Проверим вывод:
```
In [36]: table1.show()
+-------------------------+-----+
|right holder country code|count|
+-------------------------+-----+
|                       LT|  962|
|      дорога на Металл...|    6|
|                оф. 2612"|    1|
|         ул. Чистопрудная|    1|
|     347340, Ростовска...|    1|
|     109125, Москва, у...|    1|
|                       FI| 3517|
|                       AZ|  537|
|     127018, Москва, у...|    1|

```
## 3. Посчитаем самый ранний год регистрации для каждого right holder country code 
```
table2 = df.groupBy("right holder country code").min("int_reg_year")
table2.show()
table2.write.saveAsTable("min_year_country_20241124")
```
Проверим вывод:
```
In [42]: table2.show()
+-------------------------+-----------------+
|right holder country code|min(int_reg_year)|
+-------------------------+-----------------+
|                       LT|             1960|
|      дорога на Металл...|             2002|
|                оф. 2612"|             2012|
|         ул. Чистопрудная|             2020|
|     347340, Ростовска...|             1991|
|     109125, Москва, у...|             2000|
|                       FI|             1968|
|                       AZ|             1961|

```

## 4. Посчитаем самый поздний год регистрации для каждого right holder country code 
```
table3 = df.groupBy("right holder country code").max("int_reg_year")
table3.show()
table3.write.saveAsTable("max_year_country_20241124")
```
Проверим вывод:
```
In [45]: table3.show()
+-------------------------+-----------------+
|right holder country code|max(int_reg_year)|
+-------------------------+-----------------+
|                       LT|             2024|
|     690000, г. Владив...|             1995|
|     628011, г.Ханты-М...|             2017|
|     125047, Москва, М...|             1995|
|     141551, Московска...|             1995|
|                       TC|             2024|

```

## 5. Посчитаем средний год регистрации для каждого right holder country code 
```
table4 = df.groupBy("right holder country code").avg("int_reg_year")
table4.show()
table4.write.saveAsTable("avg_year_country_20241124")
```
Проверим вывод (это нормально, что некоторые числа не целые, ведь мы смотрим среднее значение):
```
In [48]: table4.show()
+-------------------------+------------------+
|right holder country code| avg(int_reg_year)|
+-------------------------+------------------+
|                       LT|1996.0873180873182|
|     690000, г. Владив...|            1995.0|
|     628011, г.Ханты-М...|            2017.0|
|     125047, Москва, М...|            1995.0|
|     141551, Московска...|            1995.0|
|                       TC|2017.6170212765958|


```

## 6. Оставим только уникальные объекты в колонке right holder name
```
table5 = df.select('right holder name').distinct()
table5.show()
table5.write.saveAsTable("unique_rholder_name_20241124")
```

## Как сохранить данные в формате партиционированной таблицы мы показали ранее
Можем еще раз повторить здесь общий template.

Количество текущих партиций:
```
In [28]: df.rdd.getNumPartitions()
Out[28]: xx
```

Их изменение:
```
df.write.parquet("your_table_name")
df = df.repartition(num_part, "yor col")
df.rdd.getNumPartitions()
df.write.saveAsTable("your_table_name", partitionBy="your col")
```
------------------------------------

