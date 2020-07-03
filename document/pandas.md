# pandas使用

官网地址: <https://pandas.pydata.org/>， 文档地址：<https://pandas.pydata.org/docs/getting_started/10min.html#min>

在Python中，pandas是基于NumPy数组构建的，使数据预处理、清洗、分析工作变得更快更简单。pandas是专门为处理表格和混杂数据设计的，而NumPy更适合处理统一的数值数组数据。
使用下面格式约定，引入pandas包：`import pandas as pd`。

pandas有两个主要数据结构：Series和DataFrame。

## Series

Series是一种类似于一维数组的对象，它由一组数据（各种NumPy数据类型）以及一组与之相关的数据标签（即索引）组成，即index和values两部分，可以通过索引的方式选取Series中的单个或一组值。

### Series的创建

`pd.Series(list,index=[ ])`

- 第一个参数可以是列表或者ndarray
- 第一个参数可以是字典，字典的键将作为Series的索引
- 第一个参数可以是DataFrame中的某一行或某一列
- 第二个参数是Series中数据的索引，可以省略。

### Series类型的操作

eries类型索引、切片、运算的操作类似于ndarray，同样的类似Python字典类型的操作，包括保留字in操作、使用.get()方法。

Series和ndarray之间的主要区别在于Series之间的操作会根据索引自动对齐数据。

## DataFrame

- DataFrame是一个表格型的数据类型，每列值类型可以不同，是最常用的pandas对象。
- DataFrame既有行索引也有列索引，它可以被看做由Series组成的字典（共用同一个索引）。
- DataFrame中的数据是以一个或多个二维块存放的（而不是列表、字典或别的一维数据结构）。

### DataFrame的创建

`pd.DataFrame(data,columns = [ ],index = [ ])`

- columns和index为指定的列、行索引，并按照顺序排列。
- 创建DataFrame最常用的是直接传入一个由等长列表或NumPy数组组成的字典，会自动加上行索引，字典的键会被当做列索引
- 如果创建时指定了columns和index索引，则按照索引顺序排列，并且如果传入的列在数据中找不到，就会在结果中产生缺失值：
- 另一种常见的创建DataFrame方式是使用嵌套字典，如果嵌套字典传给DataFrame，pandas就会被解释为外层字典的键作为列，内层字典键则作为行索引

```python
import pandas as pd
data = {'state': ['Ohio', 'Ohio', 'Ohio', 'Nevada', 'Nevada', 'Nevada'],
        'year': [2000, 2001, 2002, 2001, 2002, 2003],
        'pop': [1.5, 1.7, 3.6, 2.4, 2.9, 3.2]}
df= pd.DataFrame(data)

df2 = pd.DataFrame(data, columns=['year', 'state', 'pop', 'debt'], index=['one', 'two', 'three', 'four', 'five', 'six'])

pop = {'Nevada': {2001: 2.4, 2002: 2.9}, 'Ohio': {2000: 1.5, 2001: 1.7, 2002: 3.6}}
df3 = pd.DataFrame(pop)
```

### DataFrame对象操作

df.values：将DataFrame转换为ndarray二维数组，注意后面不加()。
通过类似字典标记的方式或属性的方式，可以将DataFrame的列获取为一个Series。
列可以通过赋值的方式进行修改。例如，我们可以给那个空的"debt"列赋上一个标量值或一组值。
将列表或数组赋值给某个列时，其长度必须跟DataFrame的长度相匹配。如果赋值的是一个Series，就会精确匹配DataFrame的索引，所有的空位都将被填上缺失值。
为不存在的列赋值会创建出一个新列。关键字del用于删除列。

### pandas的基本功能

数据索引：Series和DataFrame的索引是Index类型，Index对象是不可修改，可通过索引值或索引标签获取目标数据，也可通过索引使序列或数据框的计算、操作实现自动化对齐。索引类型index的常用方法：

- df.append(idx)：连接另一个Index对象，产生新的Index对象
- df.diff(idx)：计算差集，产生新的Index对象
- df.intersection(idx)：计算交集
- df.union(idx)：计算并集
- df.delete(loc)：删除loc位置处的元素
- df.insert(loc,e)：在loc位置增加一个元素
- df.reindex(index, columns ,fill_value, method, limit, copy )：能够改变、重排Series和DataFrame索引，会创建一个新对象，如果某个索引值当前不存在，就引入缺失值
  - index/columns为新的行列自定义索引；
  - fill_value为用于填充缺失位置的值；
  - method为填充方法，ffill当前值向前填充，bfill向后填充；
  - limit为最大填充量；
  - copy 默认True，生成新的对象，False时，新旧相等不复制
- df.drop()：能够删除Series和DataFrame指定行或列索引
- df.loc(rowTag，columnTag)：通过标签查询指定的数据，第一个值为行标签，第二值为列标签
- df.iloc(rowIndex，columnIndex)：通过默认生成的数字索引查询指定的数据
