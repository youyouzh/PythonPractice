# Stable Diffusion 本地部署教程

## 背景

2023年3月，此时AIGC已经是大家熟知的话题，通过AI来生成图片，图片的质量已经非常高，甚至能商用的地步，虽然版权纠纷啥的，手画不好等问题，不过不能否定AIGC的表现非常令人期待。

所以自己也想搭一个本地的AIGC跑一下，主流的`Stable Diffusion`开源了，据说比`Disco Diffusion`更快，可以加入`ControlNet`对生成过程做控制等。

首先要想本地能部署训练，肯定需要显卡内存要大，搭建了python、cuda等环境，安装方法参考：<https://github.com/youyouzh/PythonPractice>。

## 本地安装安装`stable-diffusion`

`stable-diffusion`开源在github上，可以到上面看安装方法：<https://github.com/CompVis/stable-diffusion>，详细来说步骤如下：

1. 克隆代码 `git clone https://github.com/CompVis/stable-diffusion.git`
2. 去到`stable-diffusion`文件夹，安装环境，执行`conda env create -f environment.yaml`，安装慢记得更换源
3. 上一步会创建一个名为`ldm`的conda虚拟环境，可以使用`conda activate ldm`切换到该虚拟环境
4. 去到<https://huggingface.co>注册账号并下载模型，搜索`stable-diffusion`，下载自己需要的版本，这儿[下载v1.5版本](https://huggingface.co/runwayml/stable-diffusion-v1-5)，下载比较慢，耐心等待
5. 下载完模型后，将模型放在`stable-diffusion\models\ldm\stable-diffusion-v1`目录下，并把模型名字改成`model.ckpt`
6. 可以直接通过命令`python scripts/txt2img.py --prompt "a professional photograph of an astronaut riding a horse" --ckpt \models\ldm\stable-diffusion-v1\model.ckpt --config configs/stable-diffusion/v2-inference-v.yaml --H 768 --W 768`生成图片

## 本地安装`stable-diffusion-webui`

参考github: <https://github.com/Stability-AI/stablediffusion>。

首先clone代码： `git clone https://github.com/Stability-AI/stablediffusion.git`。

Windows平台直接运行`webui-user.bat`即可，注意一定要使用`Python3.10`以下版本，否则安装会包找不到包的错误。

安装后需要等很久，会默认下载很多包，包括基础模型也会下载。如果要替换模型，模型放到`\stable-diffusion-webui\models\Stable-diffusion`即可。

## 模型资源

- [retry比较全的模型](https://rentry.org/sdmodels)
- [HuggingFace的Stable Diffusion模型分区](https://huggingface.co/models?other=stable-diffusion)
- [Civitai](https://civitai.com/)
- [Huggingface TI分区](https://cyberes.github.io/stable-diffusion-textual-inversion-models/)
- [Discord&TG&Reddit电报模型分享群](https://discord.com/channels/1038249716149928046/1042829185078546432)
- [reddit的 stable diffusion 社区](https://www.reddit.com/r/StableDiffusion/)

### 动漫绘图模型

- nice.ckpt [2c13a9f1]
  - 偏真实cg风格，出图视频：https://www.bilibili.com/video/BV1j84y1k78D/
  - 下载地址：https://huggingface.co/elontrump/nice/resolve/main/nice.ckpt
- momoko-e.ckpt [a2a802b2]
  - 画师：ももこ https://www.pixiv.net/users/1113943
  - 下载地址：https://huggingface.co/zxsq/momoko-e/resolve/main/momoko-e.ckpt

## ControlNet

- 预处理模型安装地址：主目录\extensions\sd-webui-controlnet\annotator
- Controlnet模型下载地址：https://huggingface.co/webui/ControlNet-modules-safetensors/tree/main
- Controlnet模型安装地址：主目录\extensions\sd-webui-controlnet\models

## 渲染参数说明

- CheckPoint文件（.ckpt）：基准模型，比如写实模型，动漫模型
- CFG强度：对Prompt的拟合强度，推荐采用15
- 迭代次数与分辨率：默认的20次迭代、512x512分辨率
- 采样方法： 动漫使用`默认值Euler a`，写实使用`DPM++ SED Karrans`
- 随机种子

## Prompt指南

标签超市： <https://tags.novelai.dev/>。

### Prompt规则

prompt描述图像如何生成的输入文本，支持语言为英文，使用逗号分割一个个关键词，表情符号，emoji，甚至一些日语都是支持的。

tag语法

- 分隔：英文逗号`,`分隔不同tag，逗号前后有空格或者换行不影响，示例`1girl,loli,long hair,low twintails（1个女孩，loli，长发，低双马尾）`
- 混合：`|`表示混合多个tag，注意混合的比例，示例`1girl,red|blue hair, long hair（1个女孩，红色与蓝色头发混合，长发）`
- 增强/减弱：`(tag:weight)`，`weight`从`0.1~100`，默认状态是`1`,低于1就是减弱，大于1就是加强，示例`(loli:1.21),(one girl:1.21),(cat ears:1.1),(flower hairpin:0.9)`
- 指数增强/减弱：`(((tag))`tag外面每加一层括号，增强`1.1`倍，`[[[tag]]]`tag外面每加一层中括号，减弱`0.91`倍
- 渐变：`[tagA:tagB:number]`，`number > 1`表示第`number`步之前为`tagA`，之后变成`tagB`，`number < 1`表示总步数的`number`为`tagA`，之后渐变为`tagB`
- 交替融合: `[tagA|tagB|tagC]`，比如`[cow|horse] in a field`就是个牛马的混合物

prompt规则：

- 越靠前的`tag`权重越大；比如景色`tag`在前，人物就会小，相反的人物会变大或半身
- 生成图片的大小会影响`Prompt`的效果，图片越大需要的`Prompt`越多，不然`Prompt`会相互污染
- 通过添加emoji达到表现效果。如😍形容表情，🖐可修手
- 权重赋予: `(Prompt A:1.5,Prompt B:1.5)`效果并不好，不如直接`(Prompt A:1.5),(Prompt B:1.5)`，彩发可以直接`(red hair:1.2),(yellow hair:1.4),(green hair:1.4)`
- 分布渲染: `[Prompt A:Prompt B:Step]`,`[Prompt A::Step]`,`[:Prompt B:Step]`，此处Step > 1时表示该组合在前多少步时做为Prompt A渲染，之后作为Prompt B渲染。Step < 1时表示迭代步数百分比

### Prompt技巧

- Prompt格式优化：简易换行三段式表达
  - 第一段：画质tag，画风tag
  - 第二段：画面主体，主体强调，主体细节概括。（主体可以是人、事、物、景）画面核心内容。第二段一般提供人数，人物主要特征，主要动作（一般置于人物之前），物体主要特征，主景或景色框架等
  - 第三段：画面场景细节，或人物细节，embedding tag。画面细节内容
- 元素同典调整版语法：质量词→前置画风→前置镜头效果→前置光照效果→（带描述的人或物AND人或物的次要描述AND镜头效果和光照）*系数→全局光照效果→全局镜头效果→画风滤镜（embedding）
- 越关键的词，越往前放，相似的同类，放在一起，只写必要的关键词

### tag描述类型

- 外表
  - 发型（呆毛，耳后有头发，盖住眼睛的刘海，低双马尾，大波浪卷发），
  - 发色（顶发金色，末端挑染彩色），
  - 面部
  - 衣服（长裙，蕾丝边，低胸，半透明，内穿蓝色胸罩，蓝色内裤，半长袖，过膝袜，室内鞋），
  - 头部（猫耳,红色眼睛），
  - 颈部（项链），
  - 手臂（露肩），
  - 胸部（贫乳），
  - 腹部（可看到肚脐），
  - 屁股（骆驼耻），
  - 腿部（长腿），
  - 脚步（裸足）
- 情绪
- 他们的姿势
  - 基础动作（站，坐，跑，走，蹲，趴，跪），
  - 头动作（歪头，仰头，低头），
  - 手动作（手在拢头发，放在胸前 ，举手），
  - 腰动作（弯腰，跨坐，鸭子坐，鞠躬），
  - 腿动作（交叉站，二郎腿，M形开腿，盘腿，跪坐），
  - 复合动作（战斗姿态，JOJO立，背对背站，脱衣服）
- 背景：室内，室外，树林，沙滩，星空下，太阳下，天气如何
- 杂项：比如NSFW，眼睛描绘详细

### Prompt收集

- 正向: masterpiece, best quality, 更多画质词，画面描述
- 反向：lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry
- nsfw（not safe for work＝涩图）

### Tag记录

- 好的画质：
- 特写镜头：closeup

## 好的prompt记录

标签超市： <https://tags.novelai.dev/>。

- 妹子奶子： <https://civitai.com/gallery/97181?reviewId=13091&infinite=false&returnUrl=%2Fmodels%2F4514%2Fpure-eros-face>
- 萝莉： <https://civitai.com/gallery/143415?reviewId=20618&infinite=false&returnUrl=%2Fmodels%2F9871%2Fchikmix>
- Lora 萝莉： <https://civitai.com/gallery/113600?modelId=9997&modelVersionId=11885&infinite=false&returnUrl=%2Fmodels%2F9997%2Fliyuu-lora>
- cn: <https://civitai.com/models/10966/cngirlycy>
- 娃娃脸： <https://civitai.com/models/9387/sen-senchan25-twitter-girl>，权重低于0.5效果好

最高画质，杰作，精美的cg，萝莉正脸，微笑，可爱精致的鼻子，精致的嘴唇，银色长发，蓝色瞳孔，光影背景，超高清，16K