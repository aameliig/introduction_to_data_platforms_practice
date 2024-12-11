#!/bin/bash
set -e

# 1. Проверка и установка virtualenv
if ! command -v virtualenv &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3-virtualenv
fi

# 2. Создание виртуальной среды
virtualenv -p python3 ~/venv
source ~/venv/bin/activate

# 3. Установка необходимых пакетов
pip3 install ipython pyspark onetl

# 4. Проверка SPARK_HOME
if [ -z "$SPARK_HOME" ]; then
    echo "Укажите путь к Spark, например: /opt/spark"
    read -p "Введите SPARK_HOME: " spark_path
    export SPARK_HOME=$spark_path
    echo "export SPARK_HOME=$spark_path" >> ~/.bashrc
fi

# 5. Установка переменных окружения для Spark
export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-*.zip:$PYTHONPATH
echo "export PYTHONPATH=$PYTHONPATH" >> ~/.bashrc

# 6. Запуск Python-скрипта
ipython -i task4_spark.py
