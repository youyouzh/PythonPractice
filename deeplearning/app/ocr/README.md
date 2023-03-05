# 开源OCR框架对比

## 背景和场景

### 需求背景

最近几天突然想看小说，起点上有，当时要付钱的，算了一下订阅所有章节需要300多块钱，啊，这！只能去什么笔趣阁之类的盗版小说里面去找，但是发现这些盗版小说格式不对，而且文章根本读不通。

听闻有段时间起点的反盗版做得比较严格，所以这些盗版小说上面有些章节根本没法阅读，所以就看能不能想办法写个爬虫能自己爬取起点小说。

起点有一项优惠：手机APP上新用户可以免费看两个星期的小说，下载了app注册了一下确实可以免费看，所以就打起了爬虫的注意。因为喜欢离线看小说，没有广告完全沉浸看。

### 尝试

首先想到的是使用Drony和Fildder进行手机APP的抓包，突破HTTPS确实能够抓取到比如获取小说列表，获取章节列表之类的接口，但是并没有抓到获取章节内容的接口，换一种方法。

然后使用安卓UI自动化的方式，使用Weditor，uiautomator2，并用USB连接手机，能够读取到手机屏幕的UI元素信息，然而不知道起点是怎么渲染的，无法获取到当前屏幕章节小说的UI元素，更别说里面的内容了。

最后只能尝试使用UI自动化截屏，然后通过OCR方式识别文章内容的方式。

~~嫌麻烦，懒得jadx反编译，甚至分析它的so库文件，指不定各种加密啥的。~~

### OCR选定

2023年了，OCR已经非常成熟，也有很多开源的OCR库，所以直接拿来用就好，不过到底识别效果怎么样就另说了。

### 需求汇总

- 起点小说手机APP截屏章节文本内容识别
- 识别内容为印刷体中文
- 需要能够识别出标点符号，还有数字（起点小说每一段后面的评论数量，需要识别后去掉）
- 识别尽量准确，错别字什么的阅读起来不得劲

## OCR识别任务

### ModelScope方案

首先想到的时候，阿里之前开源模型ModelScope上面找一找有没有现成的模型：<https://www.modelscope.cn/models?name=ocr&page=1>，其实ocr模型还是有很多的，当时看了一下大部分模型只支持识别单行文本，虽然还有模型能够对文本进行分割，但是有点麻烦，而且还有标点符号啥的，所以换一个方案。

### 其他开源OCR模型库调研

- [cnocr](https://github.com/breezedeus/cnocr)
- [Tesseract](https://github.com/tesseract-ocr/tesseract)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [chineseocr](https://github.com/chineseocr/chineseocr)
- [chineseocr_lite](https://github.com/DayBreak-u/chineseocr_lite)
- [TrWebOCR](https://github.com/alisen39/TrWebOCR)

### cnocr

基于Pytorch，有较多预定义模型，便于学习和重新训练，但是精确度不高。

### Tesseract

Tesseract 是谷歌开发并开源的图像文字识别引擎，使用python开发，支持多语言和文字，不是专门针对中文场景，相关文档是英文。

```python
# pip install pytesseract pillow
from PIL import Image
import pytesseract

image_path = r'result\example.png'
text=pytesseract.image_to_string(Image.open(image_path))
print(text)
```

在实际应用中，图像并非理想情况，还需要对图像进行一定的预处理以更好地识别。如去除椒盐噪声，去除干扰物，如在车牌识别中还会利用矩形框检测框出车牌所在位置，并放大，以更好地进行车牌号识别。

### PaddleOCR 

PaddleOCR 是百度开源的中文识别的ocr开源软件，模型专门针对中文进行训练，相关文档比较齐全，识别精度比较高，但是集于比较小众的PaddlePaddle框架。

```python
# pip install paddlepaddle shapely paddleocr

from paddleocr import PaddleOCR, draw_ocr

image_path = r'result\example.png'
ocr = PaddleOCR(use_angle_cls=True, lang='ch')
result = ocr.ocr(image_path, cls=True)
print(result)  # 数组，按行输出
```

### EasyOCR

EasyOCR 是一个用 Python 编写的 OCR 库，用于识别图像中的文字并输出为文本，支持 80 多种语言。

```python
# pip install easyocr

import easyocr

image_path = r'result\example.png'
reader = easyocr.Reader(['ch_sim'], gpu=False)
result = reader.readtext(image_path)
print(result)
```

第一次运行需要下载检测模型和识别模型，可能需要连VPN才能下载。

### chineseocr

专门针对中文进行学习和训练的模型，关的文档比较多，上手相对比较容易，复杂场景下表现一般，模型是现成的新训练难度比较大。

### TrWebOCR

部署简单，使用简单，有对应的Web页面和接口，核心模型不开源，无法进行后续训练，识别精度一般，项目不怎么活跃。

