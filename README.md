## 环境搭建

### conda安装python

强烈建议使用`Anaconda`进行`Python`环境搭建，[Anaconda下载地址](https://www.anaconda.com/download/)。

选择Python3.7+以上的Windows版本，`Anaconda`安装完成以后，还需配置相应的环境变量，下面的目录请更换为自己的conda安装目录。

- `C:\Devlope\anaconda3\Scripts`
- `C:\Devlope\anaconda3\condabin`

conda离线初见虚拟环境：`conda create -n uusama --clone base`，默认环境中有比较多常用的库，conda常用命令如下：

- 虚拟环境列表： `conda env list`
- 断网时创建： `conda create -n uusama --offline`
- 复制创建： `conda create -n uusama --clone base`
- 激活虚拟环境： `conda activate uusama`
- 添加源： `conda config --add channels`
- 移除源 `conda config --remove channels`

conda安装很慢时，更换源：

```bash
# 清华的源
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/

# 其他可选的源
# 中科大的源
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/
# 阿里云的源
conda config --add channels http://mirrors.aliyun.com/pypi/simple/

conda config --set show_channel_urls yes
```

### Pycharm配置conda

Pycharm中配置conda环境的方法：

Setting -> Project -> Project Interpreter -> Add -> Conda Environment

选择刚才创建的虚拟环境下`C:\Devlope\anaconda3\envs\uusama`的`Python.exe`即可。

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


### 单元测试运行

PyCharm 单元测试配置方法，推荐使用nose进行单元测试，避免unittest自带单测必须定义类的问题。

File -> Settings -> Tools -> Python Integrated Tools -> Testing, 选择`Nosetests`。

此时下方会有`Fix`标识，需要安装`nose`库，点击即可安装。

Pycharm会自动识别包含`test`的模块名，文件名，方法名，并可以已nose进行单元测试。
