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

Поставим pyspark и зависимости:
```
pip install pyspark
pip install onetl
pip install onetl[hdfs]
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
  hdfs = SparkHDFS(host="server_name", port=xxxx, spark=spark, cluster="test")
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

## Дополнительная задача 4. Установим AirFlow
Установим совместимую версию AirFlow:
```
pip install "apache-airflow[celery]==2.10.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.3/constraints-3.12.txt"
```
Поставим pyspark и зависимости:
```
pip install pyspark
pip install onetl
pip install onetl[hdfs]
```
Запускаем airflow:
```
airflow standalone
```
Заходим в браузере на 8080 порт, пример localhost:8080
и вводим пароль, который высветился в командной строке
Проверим, что всё работает.
Далее остановим AirFlow через Ctr+C и настроим наш DAG:
```
nano my_dag.py
```

Допишем в файл нашу логику: 
```
from __future__ import annotations

import logging
import pendulum
from airflow.models import DAG
from airflow.operators.python import PythonOperator

import urllib.request
from pyspark.sql import SparkSession
import ssl
from airflow import HDFS
from oneit.file import FileUploader

with DAG(
    "example_sag_dag",
    start_date=pendulum.datetime(2024, 12, 1, tz="UTC"),
    catchup=False,
    schedule=None,
    tags=["example"],
) as dag:
    local_data_path = "/home/hadoop/input/data.csv"

    def extract_data():
        ssl._create_default_https_context = ssl._create_unverified_context
        input_url = "https://rosoptevo.gov/opendata/7730176088-bd/data-20241101-structure-20180828.csv"
        urllib.request.urlretrieve(input_url, local_data_path)

    def load_data():
        spark = SparkSession.builder \
            .master("yarn") \
            .appName("spark-with-yarn") \
            .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
            .config("spark.hive.metastore.uris", "thrift://server_name:9083") \
            .enableHiveSupport() \
            .getOrCreate()

        hdfs = HDFS("host=server_name", port=9070)
        fu = FileUploader(connection=hdfs, target_path="/input")
        fu.run(local_data_path)

        df = spark.read.options(delimiter=",", header=True).csv("/input/data.csv")

        spark.stop()

    extract_task = PythonOperator(task_id="extract_task", python_callable=extract_data)

    load_task = PythonOperator(task_id="load_task", python_callable=load_data)

    extract_task >> load_task
```

Положим файл в примеры: 
```
cp my_dag.py airflow/lib/python3.12/site-packages/airflow/example_dags/
```

Снова запустим AirFlow:
```
airflow standalone
```



  

