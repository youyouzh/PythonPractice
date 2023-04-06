# 深度学习相关笔记

## 背景

本身是已经工作多年的后端开发人员，Python基础是有的，写过不少爬虫和工具，另外大学时候学过一些机器学习相关的算法，不过已经丢掉了。

之前一时兴起研究了一下深度学习相关的知识，不过也是浅尝辄止，没有深入，也没有动手实际去搭建一些神经网络，只停留在理论阶段。

随着AlphaGo、FaceSwap、ChatGPT、AIGC等领域的突破，让人真切感受到深度学习的潜在价值，所以此次下定决心认证进入这个领域，最起码能够搭建模型投入到实际项目中，解决一些问题。

- Image Generation/Translation：挺眼馋通过AIGC生成一些漂亮的插画，甚至能够给线稿自动上色，这无疑非常刺激我这个画渣。
- Image Classification：以前爬虫爬取的几十万张动漫插画图片，还有收集的各种素材，手动分类整理实在太痛苦了，要是能训练个模型帮我自动分类就好了。
- NLP/Speech：什么语素抽取，文本识别，工作上也会用到。百万调音师！好像生成萌萌的声音，这样就不用花那么多时间去练习伪音了

## 学习路径

1. 数学基础：微积分、线性代数、概率论，帮助理解机器学习算法
2. Python：语法知识，基础库，机器学习常用库`Numpy`、`Pandas`、`matplotlib`、`Scikit-Learn`，主流深度学习框架`TensorFlow`、`PyTorch`
3. 机器学习：主流机器学习算法，比如线性回归、逻辑回归、神经网络、SVM、PCA、聚类算法
4. 深度学习常见模型：比如`CNN`、`RNN`、`LSTM`、`GAN`等
5. 强化学习：介绍强化学习的简单原理和实例
6. 实践项目：结合几个实际的项目来做比较完整的讲解
7. 阅读论文：更深入的了解，前沿研究方向

## 2023-04-06学习路径变更

我真的太废了，本来3月份的时候计划好好的，打算开始认真学习，结果被其他事情拖住了脚步，另外加班也有点严重。

期间自己本地搭建了一个`Stable Diffusion WebUI`，搭建教程参考[Stable Diffusion 本地部署教程](./app/StableDiffusion)。花了不少时间找模型，确实能生成很多漂亮的图片。

另外工作中需要用到NLP相关实体识别的任务，做了一些简单调研，现在深度学习相关的技术变革实在太快了，各种预训练模型，大模型频频出现，以前那套什么`CNN`、`RNN`没那么火了，而且现在是讲究堆算力的时代了。

重新找准自己的定位，不是去做研究，更多的是聚焦在工程应用，基于现有模型微调，所以不用花过多的时间去深究底层原理。做一个Prompt工程师也不错哈哈。

本次直接从实践入手，而不是去学理论知识，能用理解大体原理即可，参考书籍[《动手学深度学习》](https://github.com/d2l-ai/d2l-zh)，跟着编码和实践。

同时关注细分领域的最新技术，查看技术综述文章，比如MIT的[《Understanding Deep Learning》](https://udlbook.github.io/udlbook/)。

## 学习安排

作为一个苦逼打工人，只能用业余时间来进行学习，比如通勤路上、午饭晚饭和周末等，工作日在上班路上或者休息期间主要以教材阅读，知识整理为主，周末的时候进行编码实践，一周腾出大概一半的业余时间放在上面。

以工作日有效投入时间1小时，周末投入7小时计算，每周有效投入时间12小时。有加班的话相应减少投入时间。

## 使用资料

主要包括一些书籍，github开源项目，开源库的官方文档等，还有一些在线课程。

1. 书籍：《机器学习》周志华，文字版PDF，手机阅读
2. 书籍：《神经网络与深度学习》邱锡鹏，文字版PDF，手机阅读
3. 书籍：《深度学习》Yoshua Bengio+Ian GoodFellow，文字版PDF，手机阅读
4. 途中使用到的各种库，参阅官方网站 
5. 实战：<https://paperswithcode.com/>，后期进行论文阅读和代码实践 
6. 线上开源模型库： [HuggingFace](https://huggingface.co/models)，[ModelScope](https://www.modelscope.cn/home)

其他一些资料补充：

- Python学习资料：<https://github.com/jackfrued/Python-100-Days>，大概浏览，查漏补缺，按需阅读
- 《机器学习》周志华的笔记参考：<https://github.com/Vay-keen/Machine-learning-learning-notes>
- 机器学习路径参考：<https://github.com/loveunk/machine-learning-deep-learning-notes>
- PyTorch中文文档：<https://handbook.pytorch.wiki/chapter1/1.1-pytorch-introduction.html>，学会该框架的基本使用
- 深度学习论文阅读路径：<https://github.com/floodsung/Deep-Learning-Papers-Reading-Roadmap>
