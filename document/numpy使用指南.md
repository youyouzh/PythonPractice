# numpy使用指南

Numpy(Numerical Python)是专门用来处理高维数组与矩阵运算的Python库，在深度学习中经常使用。

## 数组生成

在`NumPy`中使用`ndarray`类型表示数组，可以说它是整个库的核心。

```python
import numpy as np

# 采用列表方式创建数组
np.array([1,2,3,4])

# 采用元组方式创建数组
np.array((1,2,3,4))

# 创建多维数组
np.array([[1,2,3],[2,3,4],[4,5,6]])

# 数组生成
np.arange(1, 5, 1)  # array([1, 2, 3, 4])
np.arange(1,4,3)    # array([1])

# 随机数组生成
np.random.rand()     # 0.5999106688578982
np.random.rand(1, 3) # array([[0.52078385, 0.9358565 , 0.11207231]])
np.random.randint(0, 9, (2,3)) # array([[7, 3, 5], [3, 3, 2]])
```

- `np.arange(1, 5, 1)`
  - 生成一维数组： `array([1, 2, 3, 4])`
  - 只包含开始值，不包含结束值
  - 第一个参数为开始值，默认为0
  - 第二个参数为结束值，只有一个参数时，参数为结束值9
  - 第三个参数为步长，默认为1
- `np.linspace(0, 5, 5)`
  - 生成一维数组： `array([0. , 1.25, 2.5 , 3.75, 5. ])`
  - 默认包含结束值，endpoint=False可不包含结束值
  - 第一个参数为开始值
  - 第二个参数为结束值
  - 第三个参数**生成的元素个数**
- 随机数生成： `np.random`模块
  - `rand`: 产生0到1之间的随机数
  - `randn`: 产生符合标准正态分布的随机数
  - `randint`: 产生指定区间的随机数
  - `normal`: 产生符合正态分布的随机数
  - `uniform`: 产生符合均匀分布的随机数
  - `seed`: 产生随机数种子
  - `choice`: 从指定的样本元素中随机选择数据
  - `shuffle`: 将指定的样本元素顺序打乱
  - 以上随机数生成都可以指定生成的随机数数组维度
- `np.zeros()` :生成元素全是 0 的数组
- `np.ones()`：生成元素全是 1 的数组
- `np.zeros_like(a)`: 生成形状和 a 一样且元素全是 0 的数组
- `np.ones_like(a)`: 生成形状和 a 一样且元素全是 1 的数组

## 数组存取

通过下标即可存取数组元素，可以像操作list一样进行截断。多维数组可用多个下标访问方式。

```python
import numpy as np

a = np.array([1,2,3,4,5])
print(a[2])    # 读取： 3
print(a[:2])   # 截断： array(1,2)
print(a[::1])  # 按步长选择： array(1,3,5)
print(a[::-1]) # 翻转： array(5,4,3,2,1)
a[1] = 10
print(a[1])    # 修改值：10

a2 = np.array([[1,2,3], [4,5,6]])  # 二维数组
print(a[1,1])  # 5
print(a2[::-1,:1]) # array([[4], [1]])
```

## 常见函数使用

- reshape(): 数组维度变换
- swapaxes(): 数组维度转换
- flatten(): 数组降维
- ravel(): 数组降维
- hstack(): 水平堆叠数组
- vstack(): 垂直堆叠数组

```python
import numpy as np

# 数组维度变换： reshape，其中`-1`表示剩余的维度自动补全，变换维度元素个数不相同会抛出`ValueError`
a = np.arange(0, 10, 1) # array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
a.reshape(2, 5)         # array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])
a.reshape(2, -1)        # array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])
a.reshape(-1, 5)        # array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])


# 数组转置： swapaxes， 将第0维和第1维交换
a = np.arange(0, 10, 1).reshape(2, -1)  # array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])
a.swapaxes(0, 1)                        # array([[0, 5], [1, 6], [2, 7], [3, 8], [4, 9]])


# 三维数组
b = np.arange(8).reshape(2,2,-1)  # array([[[0, 1], [2, 3]], [[4, 5], [6, 7]]])
b.swapaxes(0, 1)         # array([[[0, 1], [4, 5]], [[2, 3], [6, 7]]])

# 数组降维
c = np.arange(8).reshape(2,2,-1)  # array([[[0, 1], [2, 3]], [[4, 5], [6, 7]]])
c.flatten()     # array([0, 1, 2, 3, 4, 5, 6, 7])
c.reshape(-1)   # array([0, 1, 2, 3, 4, 5, 6, 7])
c.ravel()       # array([0, 1, 2, 3, 4, 5, 6, 7])

# 数组堆叠
d1 = np.arange(0, 4)   # array([0, 1, 2, 3])
d2 = np.arange(4, 8)   # array([4, 5, 6, 7])
np.hstack((d1, d2))    # array([0, 1, 2, 3, 4, 5, 6, 7])
np.vstack((d1, d2))    # array([[0, 1, 2, 3], [4, 5, 6, 7]])
```

## `matrices`与`array`的区别

`Numpy matrices`必须是2维的,但是` `numpy arrays (ndarrays)` `可以是多维的（1D，2D，3D····ND）. 

`Matrix`是`Array`的一个小的分支，包含于`Array`。所以`matrix`拥有`array`的所有特性。

在numpy中`matrix`的主要优势是：相对简单的乘法运算符号。例如，a和b是两个matrices，那么`a*b`，就是矩阵积，而不用`np.dot()`，而且`matrix`的运行总是二维矩阵。

`matrix`和`array`都可以通过objects后面加`.T`得到其转置。但是`matrix objects`还可以在后面加`.H`、`.f`得到共轭矩阵, 加`.I`得到逆矩阵。

`matrix`和`array`混用会造成很多困扰，引起建议只使用一种类型，推荐`array`。

- at()函数中矩阵的乘积可以使用（星号） *  或 .dot()函数，其结果相同，而矩阵对应位置元素相乘需调用numpy.multiply()函数
- array()函数中矩阵的乘积只能使用 .dot()函数。而星号乘 （*）则表示矩阵对应位置元素相乘，与numpy.multiply()函数结果相同

## `array`使用问题记录

- (x, )表示一个`x`维向量，表示为：`a=[3, 4, 5]`
  - `np.shape(a)`: `(3, )`
  - `a.reshape(3, 1)`: a不变，结果为：`[[3], [4], [5]]`
- (x, 1)表示一个`x*1`维矩阵，表示为：`b=[[3], [4], [5]]`
  - `np.shape(b)`: `(3, 1)`
  - `b.reshape(3, )`: b不变，结果为`[3, 4, 5]`
  - `a + b`: 结果为`3x3`矩阵：`[[ 6,  7,  8], [ 7,  8,  9], [ 8,  9, 10]]`
