## Stddata爬虫
爬取www.sdtdata.com网站的标准数据的一个简单爬虫，scrapy版本2.11，教程参照https://docs.scrapy.org/en/latest/intro/tutorial.html

### 1 环境安装
#### 1.1 下载并安装Anaconda3:
miniconda3是一个方便的python版本管理工具，如果你已经有了习惯的python版本管理工具，可以不装。推荐https://docs.anaconda.com/miniconda官网下下载适合您系统的Anaconda3安装包,并按照官网提示提示进行安装。
#### 1.2 创建并激活Python 3.11环境:
```shell
conda create -n sdtdata python=3.11
conda activate sdtdata
```
#### 1.3 安装requirement依赖:
```shell
pip install -r requirements.txt
```
#### 1.4 验证环境:
```shell
python --version
```
#### 1.5 数据库:
安装mysql并执行./sdtdata.sql文件
在./sdtdata/sdtdata/settings.py中配置数据库连接信息
### 2 使用说明
直接启动爬虫：
```shell
cd sdtdata
scrapy crawl sdtdata_fx
```

### 3 项目结构
项目结构遵循标准的scarpy项目结构，如下所示：
```dtd
sdtdata/
├── sdtdata/
│   ├── __init__.py
│   ├── items.py                //定义数据结构
│   ├── middlewares.py
│   ├── piplines.py             //数据库处理
│   ├── settings.py             //项目配置文件，数据库链接配置
│   └── spiders/                //爬虫文件
│       ├── __init__.py         
│       └── sdtdata_fx.py       //爬虫主体：爬取 www.sdtdata.com/fx/fmoa/tsLibList 数据
├── main.py                     //这个main.py没有什么用主要是我用来调试的，项目启动请参照使用说明
└── scrapy.cfg                  //scrapy项目配置文件
.gitignore:
README.md:                      //项目说明文档
requirements.txt:               //项目依赖库清单
```


