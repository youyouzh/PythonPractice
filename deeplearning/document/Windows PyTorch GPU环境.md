# Windows PyTorch GPU环境

## modelscop安装

```shell
# 创建conda环境
conda create -n modelscope python=3.7
conda activate modelscope

# 安装pytorch
pip3 install torch torchvision torchaudio

# 安装pytorch-使用清华的源
pip3 install torch torchvision torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装深度学习核心框架
pip install modelscope

# 所有ModelScope平台上支持的各个领域模型功能
pip install "modelscope[audio,cv,nlp,multi-modal,science]" -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html
```

## 版本对应关系

- torch           1.12.1
- torchaudio      0.13.1
- torchmetrics    0.11.1
- torchvision     0.13.1
- python          3.7.6
- cuda            11.6.0

## cuda下载

- 查看显卡算力： [点击查看显卡算力表](https://developer.nvidia.com/cuda-gpus)，有不同显卡的算力，算力至少3.5以上才能安装CUDA
- 查看显卡驱动版本： [点击下载更新驱动](https://www.nvidia.com/Download/index.aspx)，右键空白地方 -> NIVIDIA 控制面板 -> 左下角系统消息 -> 显示 -> 查看驱动版本
- 查看显卡支持CUDA版本： [点击查看显卡驱动对于CUDA版本](https://docs.nvidia.com/cuda/archive/10.0/cuda-toolkit-release-notes/index.html)，按照步骤3，点击组件，其中有`NVCUDA.dll`，就是当前支持的CUDA版本
- 安装Visual Studio 2015、2017 和 2019 的 Microsoft Visual C++ 可再发行组件： [软件下载地址](https://support.microsoft.com/zh-cn/help/2977003/the-latest-supported-visual-c-downloads)，下载并安装`vc_redist.x64.exe`，安装完要重启
- 安装CUDA： [CUDA下载地址](https://developer.nvidia.com/cuda-toolkit-archive)，通过上面几步，找到合适自己环境版本的CUDA，**版本一定要对得上**
