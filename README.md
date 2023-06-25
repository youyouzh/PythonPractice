## 概述

### 说明

本项目是`uusama`的个人学习向python实践项目，其中主要包括：

- [python爬虫](./spider)
- [python常用工具](./tool)
- [机器学习深度学习实践](./deeplearning)
- [python自用基本库](./u_base)
- [leetcode刷题实现](./leetcode)

主要包含各种代码实现以及相关的一些文档，**本项目仅用于学习交流，请勿滥用或者用于商业用途**。

### 使用方式

直接 `git clone https://github.com/youyouzh/PythonPractice.git` 下载代码，安装相应的依赖`pip install requirements`即可运行。

### 编码规范

编码尽量遵守Python [PEP8规范](https://peps.python.org/pep-0008/)，命名规范如下：

- 项目：首字母大写+大写式驼峰, 如：`PythonPractice`
- 包、模块、文件：使用小写字母命名，多个单词之间用下划线分隔
- 类、异常：首字母大写+大写式驼峰，一个模块可保护多个类，私有类前缀下划线，如`_PrivateClassExample`
- 函数、变量：使用小写字母命名，多个单词之间用下划线分隔，私有函数名称需要以下划线开头
- 常量、全局变量：使用大写字母命名，多个单词之间用下划线分隔，私有常量名称需要以下划线开头

### 文件结构

```txt
├── leetcode        # leetcode 刷题代码
├── deeplearning    # 深度学习相关代码和文档
├── spider          # 各种爬虫代码
├── tool            # 常用基本工具
├── test            # 单元测试库
└── u_base          # 自用基本工具库
```

## Windows使用conda搭建python环境

强烈建议使用`Anaconda`进行`Python`环境搭建，可以更好的管理依赖，`Anaconda`可以同时创建多个版本的`Python`虚拟环境，非常方便。。

### conda安装python

[Anaconda下载地址](https://www.anaconda.com/download/)。 选择Python3.7+以上的Windows版本，`Anaconda`安装完成以后，还需配置相应的环境变量，下面的目录请更换为自己的conda安装目录。

**注意最新版anaconda安装的时候一定要以管理员身份安装，不然安装文件不完整，只有Lib几个文件，就一个_conda.exe，巨坑**。

- `C:\work\anaconda3\Scripts`
- `C:\work\anaconda3\condabin`

conda离线创建虚拟环境：`conda create -n uusama --clone base`，默认环境中有比较多常用的库，

如果只是创建一个纯净的新环境，可以用`conda.bat create -n uusama python3.7`。

### conda更换源

conda安装很慢或者安装报网络连接错误时，考虑更换国内的源，首选清华的源，注意更换源后更新缓存`conda clean -i`，保证用的是镜像站提供的索引。

```bash
# 清华的源
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/

# 其他可选的源
# 中科大的源
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/
# 阿里云的源
conda config --add channels http://mirrors.aliyun.com/pypi/simple/
conda config --add channels https://developer.aliyun.com/mirror/anaconda/

conda config --set show_channel_urls yes
```

window和linux一样可以通过修改home目录下的`.condarc`文件来直接修改配置，注意这个源的链接配置直接放在`channels`下，网上很多实用`default`的方式有时候不生效。

清华源（首选），官方更换方式：<https://mirror.tuna.tsinghua.edu.cn/help/anaconda/>，如果报错，则尝试修改`https`为`http`即可。

```log 
Collecting package metadata (current_repodata.json): failed

CondaHTTPError: HTTP 000 CONNECTION FAILED for url <https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/win-64/current_repodata.json>
Elapsed: -

An HTTP error occurred when trying to retrieve this URL.
HTTP errors are often intermittent, and a simple retry will get you on your way.
'https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/win-64'
```

```config
channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/Paddle/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/msys2/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/fastai/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/bioconda/
  - default
show_channel_urls: true
```

阿里源

```config
channels:
  - http://mirrors.aliyun.com/anaconda/pkgs/main
  - http://mirrors.aliyun.com/anaconda/pkgs/r
  - http://mirrors.aliyun.com/anaconda/pkgs/msys2
  - default
show_channel_urls: true
```

完整的`.condarc`文件参考如下：

```config
channels:
  - defaults
show_channel_urls: true
default_channels:
  - http://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - http://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
  - http://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  msys2: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  bioconda: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  menpo: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch-lts: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  simpleitk: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
ssl_verify: false
remote_read_timeout_secs: 5000.0
envs_dirs:
  - D:\work\conda-data\envs
pkgs_dirs:
  - D:\work\conda-data\pkgs
```

### conda修改虚拟环境安装目录

conda环境默认安装在用户目录`C:\Users\username\.conda\envs`下，如果选择默认路径，那么之后创建虚拟环境，也是安装在用户目录下。不想占用C盘空间，可以修改conda虚拟环境路径。

打开`C:\Users\username\.condarc`文件之后，添加或修改`.condarc` 中的 `env_dirs` 设置环境路径，按顺序第⼀个路径作为默认存储路径，搜索环境按先后顺序在各⽬录中查找。

```text
envs_dirs:
  - D:\work\conda-data\envs
pkgs_dirs:
  - D:\work\conda-data\pkgs
```

### conda中pip源配置

进入conda虚拟环境中，如果使用pip安装比较满，可以配置pip源为国内： `pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple`。

单个包安装使用清华源用`-i`选项： `pip install requests -i -i https://pypi.tuna.tsinghua.edu.cn/simple`。

### conda常用命令如下：

- 虚拟环境列表： `conda env list`
- 断网时创建： `conda create -n uusama --offline`
- 复制创建： `conda create -n uusama --clone base`
- 激活虚拟环境： `conda activate uusama`
- 删除环境： `conda remove -n uusama --all`
- 添加源： `conda config --add channels`
- 移除源： `conda config --remove channels`
- 删除没用的包： `conda clean -p`
- 删除所有的安装包及cache： `conda clean -y --all`
- 升级conda： `conda update conda`
- 重命名环境名（先克隆后删除）： `conda create -n newname --clone oldname && conda remove -n oldname --all`
- 已有环境导出： `conda env export --file myenv.yaml --name myenv`
- 更换环境包： `conda env update -f environment.yaml`
- 环境导入安装： `conda env create -f myenv.yaml`

### Pycharm配置conda

Pycharm是非常方便的Python相关IDE，可以下载社区免费版本，[PyCharm Community 版本下载地址](https://www.jetbrains.com/pycharm/download/)。

Pycharm中配置conda环境的方法：

Setting -> Project -> Project Interpreter -> Add -> Conda Environment

选择刚才创建的虚拟环境下`C:\work\anaconda3\envs\uusama`的`Python.exe`即可。

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
