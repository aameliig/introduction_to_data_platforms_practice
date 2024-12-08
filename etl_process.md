# Запуск ETL процесса

В этом пошаговом руководстве описано, как создать регулярного процесса чтения, трансформации и записи данных под управлением
оркестратора

## 0. Подключимся на наш сервер и запустим оболочку интерпретатора питона
Мы будем использовать интерактивную оболочку ipython.

Если у вас еще не установлена виртуальная среда для работы с python, то можно это сделать с помощью этого кода:

```
sudo apt-get install python3-virtualenv
virtualenv -p python3 ~/venv
source venv/bin/activate
pip3 install ipython
```
В дальнейшем можно начинать работу следующим образом: заходим в виртуальную среду

```
source venv/bin/activate
```


Установим необходимые пакеты:
```
pip install prefect
```

## 1. Создадим скрипт с нашим будущим ETL процессом

```
vim prefect_flow.py
```

## 2. Пишем файл с ETL процессом

Добавляем переменные окружения для спарка

```
import os, sys

for root, dirs, files in os.walk(f"{os.environ['SPARK_HOME']}/python/lib"):
    for file in files:
        if "zip" in file:
            sys.path.insert(0, os.path.join(root, file))
```

Добавляем импорты 

```
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from onetl.connection import SparkHDFS
from onetl.file import FileDFReader
from onetl.db import DBWriter
from onetl.file.format import CSV
from onetl.connection import Hive

from prefect import flow, task
```

Создаем спарк сессию

```
@task
def create_session():
  spark = SparkSession.builder \
      .master("yarn") \
      .appName("spark-with-yarn") \
      .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
      .config("spark.hive.metastore.uris", "thrift://server_name:хххх") \
      .enableHiveSupport() \
      .getOrCreate()
  return spark
```

Создаем задачу чтения данных

```
@task
def extract_data(spark):
  hdfs = SparkHDFS(host="tmpl-nn", port=9000, spark=spark, cluster="test")
  hdfs.check()
  reader = FileDFReader(connection=hdfs, format=CSV(delimiter=",", header=True), source_path="/input")
  df = reader.run(["data-20241101-structure-20180828.csv"])
  return df
```

Создаем задачу трансформации данных

```
@task
def transform_data(_df):
  df = _df.withColumn("reg_year", F.col("registration date").substr(0, 4))
  df = df.repartition(90, "reg_year")
  return df
```

Создаем задачу загрузки данных

```
@task
def load_data(_df, spark):
  hive = Hive(spark=spark, cluster="test")
  writer = DBWriter(connection=hive, table="test.regs", options={"if_exists": "replace_entire_table", "partitionBy": "reg_year"})
  writer.run(_df)
```

Создаем поток

```
@flow
def process_data():
  spark_sess = create_session()
  edata = extract_data(spark_sess)
  tdata = transform_data(edata)
  load_data(tdata, spark_sess)
```

Инициализируем запуск потока

```
if __name__ == "__main__":
  process_data()
```

## 3. Теперь мы можем выполнить процесс командой 

```
python prefect_flow.py
```
  
