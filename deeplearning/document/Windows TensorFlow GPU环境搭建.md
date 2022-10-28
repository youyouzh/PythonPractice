# Windows配置TensorFlow2.0 GPU版本环境搭建

## 安装python环境

使用anaconda安装python参考[该文档](../../README.md)。

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