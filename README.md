## 概述

### 说明

本项目是`uusama`的个人学习向python项目，其中主要包括：

- python爬虫
- python工具
- 机器学习
- python基本库
- leetcode刷题实现

主要包含各种代码实现已经相关的一些文档。

## 文件结构

```txt
├── leetcode        # leetcode 刷题代码
├── deeplearning    # 深度学习相关代码和文档
├── spider          # 各种爬虫代码
├── tool            # 常用基本工具
├── test            # 单元测试库
└── u_base          # 基本工具库
```

## Windows使用conda搭建python环境

强烈建议使用`Anaconda`进行`Python`环境搭建，可以更好的管理依赖，`Anaconda`可以同时创建多个版本的`Python`虚拟环境，非常方便。。

### conda安装python

[Anaconda下载地址](https://www.anaconda.com/download/)。 选择Python3.7+以上的Windows版本，`Anaconda`安装完成以后，还需配置相应的环境变量，下面的目录请更换为自己的conda安装目录。

- `C:\Devlope\anaconda3\Scripts`
- `C:\Devlope\anaconda3\condabin`

conda离线创建虚拟环境：`conda create -n uusama --clone base`，默认环境中有比较多常用的库，

如果只是创建一个纯净的新环境，可以用`conda.bat create -n uusama python3.7`。

### conda更换源

conda安装很慢或者安装报网络连接错误时，考虑更换源：

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

window和linux一样都是修改home目录下的.condarc文件。

阿里源

```config
channels:
  - defaults
show_channel_urls: true
default_channels:
  - http://mirrors.aliyun.com/anaconda/pkgs/main
  - http://mirrors.aliyun.com/anaconda/pkgs/r
  - http://mirrors.aliyun.com/anaconda/pkgs/msys2
custom_channels:
  conda-forge: http://mirrors.aliyun.com/anaconda/cloud
  msys2: http://mirrors.aliyun.com/anaconda/cloud
  bioconda: http://mirrors.aliyun.com/anaconda/cloud
  menpo: http://mirrors.aliyun.com/anaconda/cloud
  pytorch: http://mirrors.aliyun.com/anaconda/cloud
  simpleitk: http://mirrors.aliyun.com/anaconda/cloud
```

清华源
```config
channels:
  - defaults
show_channel_urls: true
default_channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  msys2: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  bioconda: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  menpo: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  simpleitk: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
```

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


### Pycharm配置conda

Pycharm是非常方便的Python相关IDE，可以下载社区免费版本，[PyCharm Community 版本下载地址](https://www.jetbrains.com/pycharm/download/)。

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
