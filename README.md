## Merge Insert SQL

### 简介

合并 SQL INSERT 语句，将单个语句合并成一个使其批量 INSERT,显著提高速度 。支持标准 INSERT 和带字段版本，支持命令行文件/目录参数

### 命令行用法
`python .\merge_insert_cmd.py -h`

```text
usage: merge_insert_cmd.py [-h] [-o OUTPUT] path

将多个 INSERT INTO 合并为一条 SQL 插入语句

positional arguments:
  path                  SQL 文件路径或文件夹路径

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        输出文件夹（默认：merged_sql）

```

