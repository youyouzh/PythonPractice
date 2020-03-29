# 需要扩展

- requests: 网络请求
- bs4 BeautifulSoup: html解析扩展
- 运行环境：Python3

# 主要函数

- get_content(url = '') : 获取网页或者本地页面内容
- scan_main_page(url) : 扫描文章汇总页面，获取文章链接等
- scan_article_page(url) : 扫描文章页面，获取所有图片链接以及神秘代码
- driver(url) : 开始开车，输出文章图片和神秘代码的HTML页面
