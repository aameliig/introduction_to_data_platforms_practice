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
