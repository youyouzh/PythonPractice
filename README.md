## 使用库说明

环境需要在`Python3.6`以上，只在`Windows x64`位系统性校验可行，需安装下面的包

- `wheel`: 常用的python包管理工具
- `Pillow`： 图片处理库，包含PIL，[Document](https://pillow.readthedocs.io/en/stable/installation.html)
  - 64位Windows直接安装PIL会报错： Could not find a version that satisfies the requirement PIL
- `requests`: 网络请求库，[Document](https://requests.readthedocs.io/en/master/)
- `threadpool`: 线程池处理
- `beautifulsoup4`: 网页Document解析，[Document](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- `pymysql`: mysql数据库驱动，[Document](https://pymysql.readthedocs.io/en/latest/)
- `SQLAlchemy`: ORM数据库操作，依赖`wheel`包，[Document]((https://docs.sqlalchemy.org/en/13/intro.html))

可以直接`pip install -r requirements.txt`安装所有依赖。

## 文件结构说明

```txt
├── leetcode        # leetcode 刷题代码
├── spider          # 爬虫代码
│   ├── hacg        # hacg琉璃神社网页爬虫
│   └── pixiv       # pixiv客户端API爬虫
│       ├── crawler # 爬虫代码
│       ├── mysql   # 图片数据库实体以及处理
│       │   ├── entity   # pixiv图片和用户实体
│       │   └── entity_example  # 爬虫示例数据
│       └── pixiv_api    # pixiv api封装
├── tool                 # 常用基本工具
│   ├── file_process     # 文件处理
│   └── xiaomi_note_backup
└── u_base               # 基本工具库
```

### u_base

常用的基本库。

- log.py: logging 日志封装
- u_exception.py: 异常类型封装
- u_platform.py: 平台相关函数
- unittest.py: 单元测试函数
- version.py: 关于本库的版本说明
