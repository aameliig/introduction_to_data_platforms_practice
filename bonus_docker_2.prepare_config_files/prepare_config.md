# Создание конфигурационных файлов в config.dir

**Шаг 1.** Создаем отдельную папку config для конфигурационных файлов. Набираем в консоли:
```
  mkdir config
  cd config
```

Аналогично создаем внутри папки namenode и datanode - там будут лежать соответствующие конфигурационные файлы.

**Шаг 2.** Для **namenode** cоздаем файлы **core-site.xml**

```
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://namenode:9000</value>
    </property>
</configuration>
```

и **hdfs-site.xml**:
```
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>3</value>
    </property>

    <property>
        <name>dfs.name.dir</name>
        <value>file:///hadoop/dfs/name</value>
    </property>

    <property>
        <name>dfs.data.dir</name>
        <value>file:///hadoop/dfs/data</value>
    </property>
</configuration>

```


**Шаг 3.** Аналогично, но с небольшими изменениям повторяем для **datanode** (приложено в папке).

Полные файлы можно найти в папке
