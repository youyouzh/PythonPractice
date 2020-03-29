## 琉璃神社爬虫
该爬虫将会爬取琉璃神社文章中的所有参考图片（已经去掉广告图片）还有神秘代码，包括magnet种子，以及百度盘连接等。然后将这些内容重新组织生成一个汇总的HTML页面，在该HTML页面中，去除掉多余的信息，只会展示每篇文章的标题，相关展示图片，以及神秘代码。

输入需要爬取的首页：http://www.hacg.dog/wp/category/all/game/

运行，将会在page目录下的 output.html 文件中生成爬取到的页面HTML数据。

主函数：driver(), 运行即可发车。

## 需要扩展

- requests: 网络请求
- bs4 BeautifulSoup: html解析扩展
- 运行环境：Python3

## 主要函数

- get_content(url = '') : 获取网页或者本地页面内容
- scan_main_page(url) : 扫描文章汇总页面，获取文章链接等
- scan_article_page(url) : 扫描文章页面，获取所有图片链接以及神秘代码
- driver(url) : 开始开车，输出文章图片和神秘代码的HTML页面
