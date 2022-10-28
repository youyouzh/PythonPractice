# 单元测试

## 单元测试运行

PyCharm 单元测试配置方法，推荐使用nose进行单元测试，避免unittest自带单测必须定义类的问题。

File -> Settings -> Tools -> Python Integrated Tools -> Testing, 选择`Nosetests`。

此时下方会有`Fix`标识，需要安装`nose`库，点击即可安装。

Pycharm会自动识别包含`test`的模块名，文件名，方法名，并可以已nose进行单元测试。
