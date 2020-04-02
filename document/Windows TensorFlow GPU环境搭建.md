# Windows配置TensorFlow2.0 GPU版本环境搭建

## 安装python环境

### conda安装python

强烈建议使用`Anaconda`进行`Python`环境搭建，`Anaconda`可以同时创建多个版本的`Python`虚拟环境，非常方便。[Anaconda下载地址](https://www.anaconda.com/download/)。

选择Python3.7+以上的Windows版本，`Anaconda`安装完成以后，还需配置相应的环境变量，下面的目录请更换为自己的conda安装目录。

- `C:\Devlope\anaconda3\Scripts`
- `C:\Devlope\anaconda3\condabin`

conda离线创建虚拟环境：`conda.bat create -n uusama --clone base`，默认环境中有比较多常用的库。

如果只是创建一个纯净的新环境，可以用`conda.bat create -n uusama python3.7`。

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

conda config --set show_channel_urls yes
```

### Pycharm配置conda

Pycharm是非常方便的Python相关IDE，可以下载免费版本，[PyCharm Community 版本下载地址](https://www.jetbrains.com/pycharm/download/)。

Pycharm中配置conda环境的方法：

Setting -> Project -> Project Interpreter -> Add -> Conda Environment

选择刚才创建的虚拟环境下`C:\Devlope\anaconda3\envs\uusama`的`Python.exe`即可。

### conda常用命令

windows环境可以使用`conda.bat`代替`conda`。

- 虚拟环境列表： `conda env list`
- 创建指定版本环境： `conda create -n faceswap python=3.7`
- 断网时创建： `conda create -n faceswap --offline`
- 复制环境创建： `conda create -n faceswap --clone base`
- 激活虚拟环境： `conda activate faceswap`
- 关闭当前虚拟环境： `conda deactivate`
- 删除虚拟环境： `conda remove -n faceswap --all`
- 添加源： `conda config --add channels`
- 移除源： `conda config --remove channels`
- 删除没用的包： `conda clean -p`
- 重命名环境名（先克隆后删除）： `conda create -n newname --clone oldname && conda remove -n oldname --all`

## 安装cuda

cuda是充分利用GPU来进行并行计算的框架，[NVIDIA官网cuda安装教程](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html)。

安装步骤如下：

1. 查看显卡信息： 右键我的电脑 -> 管理 -> 设备管理器 -> 显示适配器，我的是`NVIDIA GeForce GTX 1060 6GB`
2. 查看显卡算力： [点击查看显卡算力表](https://developer.nvidia.com/cuda-gpus)，有不同显卡的算力，算力至少3.5以上才能安装CUDA，我的是`6.1`
3. 查看显卡驱动版本： [点击下载更新驱动](https://www.nvidia.com/Download/index.aspx)，右键空白地方 -> NIVIDIA 控制面板 -> 左下角系统消息 -> 显示 -> 查看驱动版本，我的是`432.00`
4. 查看显卡支持CUDA版本： [点击查看显卡驱动对于CUDA版本](https://docs.nvidia.com/cuda/archive/10.0/cuda-toolkit-release-notes/index.html)，按照步骤3，点击组件，其中有`NVCUDA.dll`，就是当前支持的CUDA版本，我的是`NVIDIA CUDA 10.1.120 driver`
5. 查看TensorFlow需要的CUDA版本： [点击查看TensorFlow需要CUDA版本](https://tensorflow.google.cn/install/source_windows)，我要安装TensorFlow最新版，`TensorFlow 2.1.0`，支持`CUDA 10.1`
6. 安装Visual Studio 2015、2017 和 2019 的 Microsoft Visual C++ 可再发行组件： [软件下载地址](https://support.microsoft.com/zh-cn/help/2977003/the-latest-supported-visual-c-downloads)，下载并安装`vc_redist.x64.exe`，安装完要重启，如果不安装，在`import tensorflow`时会报出缺少DLL的错误
7. 安装CUDA： [CUDA下载地址](https://developer.nvidia.com/cuda-toolkit-archive)，通过上面几步，找到合适自己环境版本的CUDA，**版本一定要对得上**，我的是`cuda_10.1.243_426.00_win10.exe`，千万别下载`10.2`的，巨坑
8. CUDA的安装选自定义，然后组件都选上，安装完成后添加CUDA环境变量，默认安装在`C:\Program Files\NVIDIA GPU Computing Toolkit\`添加环境变量如下：
  1. C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\bin
  2. C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\extras\CUPTI\lib64
  3. C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\include
  4. C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\libnvvp
9. 下载`cuDNN SDK`： [cuDNN SDK下载地址](https://developer.nvidia.com/rdp/cudnn-download)，TensorFlow需要安装7.6以上版本，注意版本还要匹配CUDA，我的是`Download cuDNN v7.6.5 (November 5th, 2019), for CUDA 10.1`
10. 安装`cuDNN SDK`，将下载的`cuDNN`解压，将所有文件拷贝到`CUDA Toolkit`路径下面的文件夹中，我的是`C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1`
11. 测试是否安装成功： 启动cmd，输入`nvcc -V`如果出现版本号，则安装成功

## 安装TensorFlow

可以参考官网文档继续安装: <https://tensorflow.google.cn/install/gpu>，这儿直接使用pip安装最新版：

`pip install tensorflow`，我这儿安装的版本是`tensorflow 2.1.0`。

校验TensorFlow-gpu是否安装成功：

```python
import tensorflow as tf

tf.test.is_gpu_available()
print("GPU Available: ", tf.test.is_gpu_available()) # 输出true表示安装成功并可以使用gpu
```

如果出现错误，可以去官网查看issue，很多人遇到相同的错误：<https://www.tensorflow.org/install/errors>。其中强调一下：

导入的时候`ImportError: DLL load failed`，报错，很有可能是`Microsoft Visual C++ 可再发行组件`没有安装导致的。