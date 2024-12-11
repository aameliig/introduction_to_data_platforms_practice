import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from onetl.connection import SparkHDFS
from onetl.file import FileDFReader
from onetl.file.format import CSV

# 1. Настройка пути Spark
SPARK_HOME = os.getenv("SPARK_HOME")
if not SPARK_HOME:
    raise EnvironmentError("SPARK_HOME не настроен. Установите переменную окружения.")

# Добавление путей для Spark
for root, dirs, files in os.walk(f"{SPARK_HOME}/python/lib"):
    for file in files:
        if "zip" in file:
            sys.path.insert(0, os.path.join(root, file))

# 2. Создание Spark-сессии
spark = SparkSession.builder \
    .master("yarn") \
    .appName("spark-with-yarn") \
    .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
    .config("spark.hive.metastore.uris", "thrift://server_name:10000") \
    .enableHiveSupport() \
    .getOrCreate()

# 3. Подключение к HDFS
hdfs = SparkHDFS(host="server_name", port=9000, spark=spark, cluster="test")
if not hdfs.check():
    raise ConnectionError("Не удалось подключиться к HDFS.")

# 4. Чтение файла
reader = FileDFReader(connection=hdfs, format=CSV(delimiter=",", header=True), source_path="/input")

df = reader.run(["your_file_name.csv"])

# 5. Базовый обзор данных
print("Количество строк в файле:", df.count())
print("Схема данных:")
df.printSchema()

# 6. Трансформации данных
df = df.withColumn("reg_year", F.col("registration date").substr(0, 4))
df = df.na.fill({"correspondence address": "unknown"})
df = df.withColumn(
    'sound_filled',
    F.when((F.col("sound") == 'false') | (F.col("sound").isNull()), "Нет").otherwise(F.col("sound"))
)

# 7. Сохранение данных
df.write.saveAsTable("your_table_name")
df.write.parquet("your_table_name")

# Сохранение с партиционированием
df = df.repartition(15, "reg_year")
df.write.saveAsTable("your_table_name_partitioned")

# 8. Завершение работы
spark.stop()
