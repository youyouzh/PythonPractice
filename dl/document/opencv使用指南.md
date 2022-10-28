# opencv使用指南

## opencv简介

它是一款由 Intel 公司俄罗斯团队发起并参与和维护的一个计算机视觉处理开源软件库。

多数模块基于 C++实现，少部分基于C 语言实现，同时ᨀ供了 Python、Ruby、MATLAB等语言的接口。

可自由地运行在 Linux、Windows 和 Mac OS 等桌面平台，Android、 IOS、BlackBerray 等移动平台。

OpenCV 可以完成几乎所有的图像处理任：

- 视频分析(Video analysis)
- 3D 重建(3D reconstruction)
- 特征ᨀ取(Feature extraction)
- 目标检测(Object detection)
- 机器学习(Machine learning)
- 计算摄影(Computational photography)
- 形状分析(Shape analysis)
- 光流算法(Optical flow algorithms)
- 人脸和目标识别(Face and object recognition)
- 表面匹配(Surface matching)
- 文本检测和识别(Text detection and recognition)

### opencv使用

- 安装： `pip install opencv-python`
- 导入： `import cv2`

### 官方资源导航

- OpenCV Docs 官方文档: <https://docs.opencv.org/>
- github地址： <https://github.com/opencv/opencv>
- 中文教程：<http://www.opencv.org.cn/opencvdoc/2.3.2/html/doc/tutorials/tutorials.html>

### opencv模块

- `core`模块实现了最核心的数据结构及其基本运算，如绘图函数、数组操作相关函数，与OpenGL 的互操作等。
- `highgui`模块实现了视频与图像的读取、显示、存储等接口。
- `imgproc`模块实现了图像处理的基础方法，包括图像滤波、图像的几何变换、平滑、阈值分割、形态学处理、边缘检测、目标检测、运动分析和对象跟踪等
- `features2d`模块用于提取图像特征以及特征匹配，
- `nonfree`模块实现了一些专利算法，如 sift 特征。
- `objdetect`模块实现了一些目标检测的功能，经典的基于`Haar`、LBP`特征的人脸检测，基于 HOG 的行人、汽车等目标检测，分类器使用 Cascade Classification（级联分类）和Latent SVM 等。
- `stitching`模块实现了图像拼接功能。
- `FLANN`模块（Fast Library for Approximate Nearest Neighbors），包含快速近似最近邻搜索 FLANN 和聚类 Clustering 算法。
- `ml`模块机器学习模块（SVM，决策树，Boosting 等等）。
- `photo`模块包含图像修复和图像去噪两部分。
- `video`模块针对视频处理，如背景分离，前景检测、对象跟踪等。
- `calib3d`模块即 Calibration（校准）3D，这个模块主要是相机校准和三维重建相关的内容。包含了基本的多视角几何算法，单个立体摄像头标定，物体姿态估计，立体相似性算法，3D 信息的重建等等。
- `G-API`模块包含超高效的图像处理`pipeline`引擎

另外，原来在`opencv2`中的`shape`,`superres`,`videostab`,`viz`等模块被移动到`opencv_contrib`中。

### opencv基本数据结构

- 矩阵`Mat`类：矩阵的形式来存储数据
  - dims：表示矩阵 M 的维度，如 2*3 的矩阵为 2 维，3*4*5 的矩阵为 3 维
  - data：uchar 型的指针，指向内存中存放矩阵数据的一块内存
  - rows, cols：矩阵的行数、列数
  - type：表示了矩阵中元素的类型(depth)与矩阵的通道个数(channels)
    - 命名规则为 CV_ + (位数）+（数据类型）+（通道数）
    - 其中：U（unsigned integer）-- 无符号整数
    - S（signed integer）-- 有符号整数
    - F（float）-- 浮点数
    - 例如 CV_8UC3，可拆分为：CV_：type 的前缀
    - 8U：8 位无符号整数(depth)，C3：3 通道(channels)
  - depth：即图像每一个像素的位数(bits)
    - 这个值和`type`是相关的
    - 例如`CV_8UC3`中`depth`则是`CV_8U`
  - channels：通道数量
    - 若图像为 RGB、HSV 等三通道图像，则 channels = 3；
    - 若图像为灰度图，则为单通道，则 channels = 1
  - elemSize：矩阵中每一个元素的数据大小
    - elemSize = channels * depth / 8
    - 例如：type 是 CV_8UC3，elemSize = 3 * 8 / 8 = 3bytes
  - elemSize1：单通道的矩阵元素占用的数据大小
    - elemSize1 = depth / 8
    - 例如：type 是 CV_8UC3，elemSize1 = 8 / 8 = 1bytes
- 点`Point`类：包含两个整型数据成员 x 和 y，即坐标点
- 尺寸`Size`类：数据成员是 width 和 height，一般用来表示图像的大小，或者矩阵的大小
- 矩形R`Rect`类：数据成员 x,y,width,height，分别代表这个矩形左上角的坐标点和矩形的宽度和高度
- 颜色`Scalar`类：Scalar_(_Tp v0, _Tp v1, _Tp v2=0, _Tp v3=0)
  - v0---表示 RGB 中的 B（蓝色）分量
  - v1---表示 RGB 中的 G（绿色）分量
  - v2---表示 RGB 中的 R（红色）分量
  - v3---表示 Alpha 是透明色分量
- 向量`Vec`类：Vec<int,n>---就是用类型 int 和向量模板类做一个实例化
- `Range`类：用于指定一个连续的子序列，例如一个轮廓的一部分，或者一个矩阵的列空间

### opencv基本IO操作

- 图像读写
  - `cv2.imread(filename, show_control_params)` # 读入图像
  - `cv2.imshow(window_name，image_name)` #显示图像
  - `cv2.imwrite(file_path, filename)` #保存图像
  - `cv2.namedWindow(window_name)` #创建窗口
  - `cv2.destroyAllWindows()` #销毁窗口
  - `cv2.waitKey([,delay])` #decay ＞ 0 等待 delay 毫秒， #decay ＜ 0 等待键盘单击， #decay = 0 无限等待
- 图像缩放
  - `dst = cv2.resize(src,dsize,fx,fy)` #dsize 表示缩放大小
  - #fx，fy 缩放比例
- 图像翻转
  - `dst = cv2.flip(src,flipCode)`
  - #flipCode=0 以 X 轴为对称轴的翻转
  - #lipCode＞0 以 Y 轴为对称轴的翻转
  - #flipCode＜0 对 X、Y 轴同时翻转
- 通道拆分与合并
  - `b,g,r = cv2.split(image_object)`
  - `b = cv2.split(image_object)[channel_count]` #拆分
  - `bgr = cv2.merge([b,g,r])` #合并
