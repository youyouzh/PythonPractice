## 概述

### 说明

本项目是`uusama`的个人学习向python实践项目，其中主要包括：

- [python爬虫](./spider)
- [python常用工具](./tool)
- [python自用基本库](./u_base)
- [leetcode刷题实现](./leetcode)

主要包含各种代码实现以及相关的一些文档，**本项目仅用于学习交流，请勿滥用或者用于商业用途**。

### 使用方式

直接 `git clone https://github.com/youyouzh/PythonPractice.git` 下载代码，安装相应的依赖`pip install requirements`即可运行。

### 编码规范

编码尽量遵守Python [PEP8规范](https://peps.python.org/pep-0008/)，命名规范如下：

- 项目：首字母大写+大写式驼峰, 如：`PythonPractice`
- 包、模块、文件：使用小写字母命名，多个单词之间用下划线分隔，如`file_util.py`  
- 类、异常：首字母大写+大写式驼峰，一个模块可包含多个类，私有类前缀下划线，如`_PrivateClassExample`
- 函数、变量：使用小写字母命名，多个单词之间用下划线分隔，私有函数名称需要以下划线开头，如`get_file_size`
- 常量、全局变量：使用大写字母命名，多个单词之间用下划线分隔，私有常量名称需要以下划线开头，如`HTTP_TIMEOUT`

### 文件结构

```txt
├── leetcode        # leetcode 刷题代码
├── spider          # 各种爬虫代码
├── tool            # 常用基本工具
├── test            # 单元测试库
└── u_base          # 自用基本工具库
```

### 常用包功能说明

- `wheel`: 常用的python包管理工具
- `nose`: 非常方便的单元测试框架
- `Pillow`： 图片处理库，包含PIL，[Document](https://pillow.readthedocs.io/en/stable/installation.html)
  - 64位Windows直接安装PIL会报错： Could not find a version that satisfies the requirement PIL
- `requests`: 网络请求库，[Document](https://requests.readthedocs.io/en/master/)
- `threadpool`: 线程池处理
- `beautifulsoup4`: 网页Document解析，[Document](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- `pymysql`: mysql数据库驱动，[Document](https://pymysql.readthedocs.io/en/latest/)
- `SQLAlchemy`: ORM数据库操作，依赖`wheel`包，[Document]((https://docs.sqlalchemy.org/en/13/intro.html))

可以直接`pip install -r requirements.txt`安装所有依赖。
