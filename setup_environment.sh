#!/bin/bash
set -e

# Устанавливаем venv
if ! command -v virtualenv &> /dev/null; then
    echo "Installing virtualenv..."
    sudo apt-get update && sudo apt-get install -y python3-virtualenv
fi

# Создаём виртуальную среду
echo "Creating virtual environment..."
virtualenv -p python3 ~/venv

# Активируем нашу среду
echo "Activating virtual environment..."
source ~/venv/bin/activate

# Установим интерактивный питон
echo "Installing ipython..."
pip3 install ipython pyspark

echo "Setup complete. To start, run:"
echo "source ~/venv/bin/activate && ipython"
