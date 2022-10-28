# skimage使用

官网API文档： <https://scikit-image.org/docs/0.16.x/api/api.html>

## 介绍

scikit-image是基于scipy的一款图像处理包，全称是scikit-image SciKit (toolkit for SciPy) ，它对scipy.ndimage进行了扩展，提供了更多的图片处理功能。它是由python语言编写的，由scipy 社区开发和维护。skimage包由许多的子模块组成，各个子模块提供不同的功能。主要子模块列表如下：

| 子模块名称   | 主要实现功能                                                |
| :----------- | :---------------------------------------------------------- |
| io           | 读取、保存和显示图片或视频                                  |
| data         | 提供一些测试图片和样本数据                                  |
| color        | 颜色空间变换                                                |
| filters      | 图像增强、边缘检测、排序滤波器、自动阈值等                  |
| draw         | 操作于numpy数组上的基本图形绘制，包括线条、矩形、圆和文本等 |
| transform    | 几何变换或其它变换，如旋转、拉伸和拉东变换等                |
| morphology   | 形态学操作，如开闭运算、骨架提取等                          |
| exposure     | 图片强度调整，如亮度调整、直方图均衡等                      |
| feature      | 特征检测与提取等                                            |
| measure      | 图像属性的测量，如相似性或等高线等                          |
| segmentation | 图像分割                                                    |
| restoration  | 图像恢复                                                    |
| util         | 通用函数                                                    |

## 基本使用

### 图片读取

读取单张彩色rgb图片，使用skimage.io.imread（fname）函数,带一个参数，表示需要读取的文件路径。显示图片使用skimage.io.imshow（arr）函数，带一个参数，表示需要显示的arr数组（读取的图片以numpy数组形式计算）。

```python
from skimage import io,data
img=io.imread('d:/dog.jpg')
io.imshow(img)

# 读取灰度图片
img=io.imread('d:/dog.jpg',as_grey=True)
io.imshow(img)

# 读取自带图片
img=data.lena()
io.imshow(img)

# 保存图片
img = data.chelsea()
io.imshow(img)
io.imsave('d:/cat.jpg',img)
```

skimage程序自带了一些示例图片，如果我们不想从外部读取图片，就可以直接使用这些示例图片：

- astronaut 航员图片
- coffee 一杯咖啡图片
- lena lena美女图片
- camera 拿相机的人图片
- coins 硬币图片  
- moon 月亮图片
- checkerboard 棋盘图片
- horse 马图片
- page 书页图片
- chelsea   小猫图片
- hubble_deep_field 星空图片
- text 文字图片
- clock 时钟图片 
- immunohistochemistry 结肠图片

### 图片信息

```python
from skimage import io, data

img = data.chelsea()
io.imshow(img)
print(type(img))  #显示类型
print(img.shape)  #显示尺寸
print(img.shape[0])  #图片高度
print(img.shape[1])  #图片宽度
print(img.shape[2])  #图片通道数
print(img.size)   #显示总像素个数
print(img.max())  #最大像素值
print(img.min())  #最小像素值
print(img.mean()) #像素平均值
print(img[0][0])#图像的像素值
```

### 图像像素的访问与裁剪

图片读入程序中后，是以numpy数组存在的。因此对numpy数组的一切功能，对图片也适用。对数组元素的访问，实际上就是对图片像素点的访问。

彩色图片访问方式为：img[i,j,c]
i表示图片的行数，j表示图片的列数，c表示图片的通道数（RGB三通道分别对应0，1，2）。坐标是从左上角开始。

灰度图片访问方式为：gray[i,j]

```python
from skimage import io,data,color
import numpy as np

# 输出小猫图片的G通道中的第20行30列的像素值
img=data.chelsea()
pixel=img[20,30,1]
print(pixel)

# 显示红色单通道图片
img=data.chelsea()
R=img[:,:,0]
io.imshow(R)

# 对小猫图片随机添加椒盐噪声
img=data.chelsea()

#随机生成5000个椒盐
rows,cols,dims=img.shape
for i in range(5000):
    x=np.random.randint(0,rows)
    y=np.random.randint(0,cols)
    img[x,y,:]=255
io.imshow(img)

# 对小猫图片进行裁剪
img=data.chelsea()
roi=img[80:180,100:200,:]
io.imshow(roi)

# 将lena图片进行二值化，像素值大于128的变为1，否则变为0
img=data.lena()
img_gray=color.rgb2gray(img)
rows,cols=img_gray.shape
for i in range(rows):
    for j in range(cols):
        if (img_gray[i,j]<=0.5):
            img_gray[i,j]=0
        else:
            img_gray[i,j]=1
io.imshow(img_gray)
```