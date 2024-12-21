# Пример работы с GreenPlum

В этом пошаговом руководстве описано, как загрузить файл на сервер, запустить gpfdist и создать External и Internal table

## 1. Подключение
Подключаемся к серверу стандартно, по протоколу ssh и вводим пароль

```
ssh username@<IP-адрес>
```

## 2. Работа с утилитой pyspark
Psql – стандартный клиент для Postgres, который работает и с GreenPlum. Утилита psql уже предустановлена в системе.

Заходим в консоль psql
```
psql
```

Если bash не видит утилиту psql, то нужно выполнить команду:

`source /usr/local/greenplum-db/greenplum_path.sh`

Команда `\d` в psql выводит список всех таблиц, представлений и последовательностей в БД


## 3. Подключаемся к конкретной базе данных
```
psql -d your_db_name
```
пример:
```
psql -d idp
```

## 4. Копируем данные на сервер
По предположению, мы располагаем данными (`.csv` таблицей), которые находятся у нас на компьютере. Нам нужно перенести их на сервер.
Открываем новое окно терминала и вводим команду:

```
scp your_table.csv username@<IP-адрес>:~
```

Для примера мы взяли opensource датасет для машинного обучения классификации пингвинов `penguins.csv`.

Он содержит в себе информацию о конкретных особях: длину клюва, глубину клюва, длину крыла, массу тела и пренадлежность
к определенному виду (закодирована числами integer).

Заметим, что колонки culmenlength и culmendepth содержат значения типа `float`.

```
culmenlength | culmendepth | flipperlength | bodymass | species
--------------+-------------+---------------+----------+---------
       39.100 |      18.700 |           181 |     3750 |       0
       39.500 |      17.400 |           186 |     3800 |       0
       40.300 |      18.000 |           195 |     3250 |       0
```

В нашем случае:
```
scp team_1_penguins.csv user@<IP-адрес>:~
```

## 5. Запускаем gpfdist
В этом же окне терминала подключаемся к серверу и запускаем gpfdist:

```
gpfdist
```

## 6. Создаем External table
Возвращаемся в терминал с psql. Используем синтаксис:

```
CREATE EXTERNAL TABLE team_1_penguins (
    column1 type1,
    column2 type2,
    ...
)
LOCATION('gpfdist://localhost:8080/your_table.csv')
FORMAT 'CSV' (DELIMITER ',' HEADER);
```

В нашем случае:
```
idp=> CREATE EXTERNAL TABLE team_1_penguins (
    CulmenLength numeric(10, 3),
    CulmenDepth numeric(10, 3),
    FlipperLength integer,
    BodyMass integer,
    Species integer
)
LOCATION('gpfdist://localhost:8080/team_1_penguins.csv')
FORMAT 'CSV' (DELIMITER ',' HEADER);
NOTICE:  HEADER means that each one of the data files has a header row
CREATE EXTERNAL TABLE
```

## 6. Проверка
Команды `select count(*) from your_table;` и `select * from your_table;` должны работать корректно:

```
idp=> select count(*) from team_1_penguins;
NOTICE:  HEADER means that each one of the data files has a header row
 count
-------
   344
(1 row)
```
```
idp=> select * from team_1_penguins;
NOTICE:  HEADER means that each one of the data files has a header row
 culmenlength | culmendepth | flipperlength | bodymass | species
--------------+-------------+---------------+----------+---------
       39.100 |      18.700 |           181 |     3750 |       0
       39.500 |      17.400 |           186 |     3800 |       0
       40.300 |      18.000 |           195 |     3250 |       0
              |             |               |          |       0
       36.700 |      19.300 |           193 |     3450 |       0
       39.300 |      20.600 |           190 |     3650 |       0
       38.900 |      17.800 |           181 |     3625 |       0
       39.200 |      19.600 |           195 |     4675 |       0
       34.100 |      18.100 |           193 |     3475 |       0

```

## 7. Создаем Internal table
`create table your_table_internal as select * from your_table;`

У нас:
```
idp=> create table team_1_penguins_internal as select * from team_1_penguins;
NOTICE:  Table doesn't have 'DISTRIBUTED BY' clause. Creating a NULL policy entry.
NOTICE:  HEADER means that each one of the data files has a header row
SELECT 344
```

## 7. Проверка
Проверим, что таблица появилась в бд: 

(приведен фрагмент вывода)
```

                            List of relations
 Schema |           Name            |     Type      |  Owner   | Storage
--------+---------------------------+---------------+----------+---------
 public | team_1_penguins           | foreign table | user     |
 public | team_1_penguins_internal  | table         | user     | heap
 public | хххххххххххххххх          | foreign table | user     |
 .........

```

И проверим работоспособность команды `select`:
```
idp=> select * from team_1_penguins_internal;
 culmenlength | culmendepth | flipperlength | bodymass | species
--------------+-------------+---------------+----------+---------
       39.500 |      17.400 |           186 |     3800 |       0
       39.200 |      19.600 |           195 |     4675 |       0
       37.800 |      17.300 |           180 |     3700 |       0

```

---------------------------------

