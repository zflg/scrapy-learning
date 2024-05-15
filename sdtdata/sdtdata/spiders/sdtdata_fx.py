import json
import scrapy
from sdtdata.items import SdtdataItem

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/123.0.0.0 "
              "Safari/537.36")


class SdtdataFxSpider(scrapy.Spider):
    name = "sdtdata_fx"
    allowed_domains = ["sdtdata.com"]
    # login info
    login_url = "https://sdtdata.com/fx/foodcodex?p=login&s=fcv1&act=doLogin"
    login_params = {
        "userNameLogin": "17323000617",
        "userPwdLogin": "Liuyanqi1",
        "isEncrypt": "2"
    }
    # index info
    index_url = "https://sdtdata.com/fx/fcv1/tsLibList"
    # search info
    search_url = "https://www.sdtdata.com/fx/foodcodex?p=tsLibList&s=fmoa&act=doSearch"
    # detail info
    detail_url = "https://www.sdtdata.com/fx/fmoa/tsLibCard/{}.html"

    def extract_standard(self, response, h3_text):
        # 使用 XPath 选择器定位 <h3 class="mt20">现行标准</h3> 元素
        h3_element = response.xpath(f'//h3[contains(text(), "{h3_text}")]')
        # 定位 <h3> 元素后面紧接着的第一个 ul 元素
        ul_element = h3_element.xpath('following-sibling::ul[1]')
        # 使用XPath选择器提取 ul 标签下的所有 li 元素
        li_elements = ul_element.xpath('.//li')
        standards = []
        # 提取 li 元素的文本内容
        for li in li_elements:
            # 使用 XPath 选择器定位 li 元素下的 a 元素
            a_element = li.xpath('.//a')
            # 提取 _tsId 属性值
            ts_id = a_element.xpath('./@_tsid').get()
            # 提取文本内容
            text = a_element.xpath('string()').get()
            # 如果 ts_id为空，就跳过
            self.logger.info(f"inner_id: {response.meta['item']['inner_id']},ts_id:{ts_id}, text:{text}")
            if not ts_id:
                continue
            else:
                self.logger.info(f"ts_id:{ts_id}, text:{text}")
                standard = {"inner_id": ts_id, "no": text}
                standards.append(standard)
        return standards

    def start_requests(self):
        # login x-www-form-urlencoded
        yield scrapy.FormRequest(url=self.login_url,
                                 headers={'User-Agent': USER_AGENT},
                                 formdata=self.login_params,
                                 callback=self.parse_login)
        # index
        # yield scrapy.Request(url=self.index_url,
        #                      headers={'User-Agent': USER_AGENT,
        #                               'Cookie': 'JSESSIONID=aaaJKiG3Cr61S8U27W95y'},
        #                      callback=self.parse_index)
        # search
        # print(f"search_params:{self.search_params}")
        # yield scrapy.FormRequest(url=self.search_url,
        #                          headers={'User-Agent': USER_AGENT,
        #                                   'Cookie': 'JSESSIONID=aaaJKiG3Cr61S8U27W95y'},
        #                          formdata=self.search_params,
        #                          callback=self.parse_search)
        # detail
        # yield scrapy.Request(url=self.detail_url.format("183746"),
        #                      headers={'User-Agent': USER_AGENT,
        #                               'Cookie': 'JSESSIONID=aaaJKiG3Cr61S8U27W95y'},
        #                      callback=self.parse_detail,
        #                      meta={'item': {"inner_id": "183746"}})

    def parse_login(self, response):
        self.logger.info("login success")
        # get session id
        # [b'fcPwd=1cc01f27c0e35c3e7f8e1f7a03a42424; expires=Thu, 01-Dec-1994 16:00:00 GMT', b'fcRemberPwd=1; expires=Thu, 01-Dec-1994 16:00:00 GMT', b'fcLogin=yanqi; expires=Thu, 01-Dec-1994 16:00:00 GMT', b'JSESSIONID=aaa9trGI2RSPy83_hX95y; path=/']
        cookies = response.headers.getlist('Set-Cookie')
        session_id = cookies[-1].decode().split(';')[0].split('=')[-1]
        response.meta['session_id'] = session_id
        yield scrapy.FormRequest(url=self.index_url,
                                 headers={'User-Agent': USER_AGENT,
                                          'Cookie': 'JSESSIONID=' + response.meta['session_id']},
                                 callback=self.parse_index,
                                 meta=response.meta)

    def parse_index(self, response):
        self.logger.info("index success")
        # 使用 XPath 选择器定位<textarea name="prodTypeJson" id="prodTypeJson">content</textarea> 元素里面的content
        prod_types_textarea_content = response.xpath('//textarea[@name="prodTypeJson"]//text()').get()
        # 使用 json.loads() 方法将 content 反序列化为 Python list 对象
        prod_types = json.loads(prod_types_textarea_content)
        yield from self.prod_types_iter(response, prod_types)

    # 遍历 prod_types 列表 prod_types的每一个元素都有可能含有children，而children也是一个prod_types列表
    def prod_types_iter(self, response, prod_types):
        for prod_type in prod_types:
            # 如果当前 prod_type 含有 children，就递归调用 prod_types_iter() 方法
            if "children" in prod_type:
                self.prod_types_iter(response, prod_type["children"])
            if prod_type["fcTypeCode"] is None or prod_type["fcTypeCode"] == "":
                continue
            search_params = {
                "fcTypeCode": prod_type["fcTypeCode"],
                "seniorSearch": "["
                # "{'field': 'TS_VALIDITY', 'rule': 'equal', 'disp': '有效性', 'value': '现行'}, "
                # "{'field': 'TS_COUNTRY', 'rule': 'equal', 'disp': '国别', 'value': '中国'}, "
                                "{'field': 'TS_RELEASE_DATE', 'rule': 'between', 'disp': '发布日期', 'value': '2023-05-01', 'value2': '2024-05-24'}"
                                "]",
                "isCurrent": "2",
                "isCompulsive": "2",
                "pageNum": "1"
            }
            self.logger.info(f"search params:{search_params}")
            yield scrapy.FormRequest(url=self.search_url,
                                     headers={'User-Agent': USER_AGENT,
                                              'Cookie': 'JSESSIONID=' + response.meta['session_id']},
                                     formdata=search_params,
                                     callback=self.parse_search,
                                     meta={'search_params': search_params,
                                           'session_id': response.meta['session_id']})

    def parse_search(self, response):
        self.logger.info("search success")
        # body is json
        body = json.loads(response.text)
        if body["retCode"] != "200":
            self.logger.error("Failed to search standards")
            return
        counts = body["data"]["counts"]
        hasMore = body["data"]["hasMore"] == "true"
        search_params = response.meta["search_params"]
        self.logger.info(f"product type {search_params['fcTypeCode']}, counts:{counts}, hasMore:{hasMore}")
        fetch_counts = response.meta["fetch_counts"] if "fetch_counts" in response.meta else 0
        # 转化成标准的item
        for body_item in body["data"]["datas"]:
            """
                {
                    "TS_SHOP_URL": "",
                    "TS_IMPLEMENT_DATE": "2023-05-11",
                    "TS_HAS_FILE": "yes",
                    "$ROW_NUM$": "2",
                    "TS_NO": "GB 2763.1-2022",
                    "TS_NAME": "食品安全国家标准 食品中2,4-滴丁酸钠盐等112种农药最大残留限量",
                    "$TABLE_CODE$": "V_FC_TS_LIB",
                    "TS_VIEWS": "11670",
                    "$PK_CODE$": "194155`yes",
                    "TS_PUBLISH_DEPT": "国家卫生健康委&农业农村部&市场监管总局",
                    "TS_VALIDITY": "现行",
                    "TS_ID": "194155",
                    "TS_RELEASE_DATE": "2022-11-11"
                }
            """
            item = SdtdataItem()
            item["inner_id"] = body_item["TS_ID"]
            item["no"] = body_item["TS_NO"]
            item["table_code"] = body_item["$TABLE_CODE$"]
            item["name"] = body_item["TS_NAME"]
            item["release_date"] = body_item["TS_RELEASE_DATE"]
            item["implement_date"] = body_item["TS_IMPLEMENT_DATE"]
            item["has_file"] = body_item["TS_HAS_FILE"]
            item["is_validity"] = body_item["TS_VALIDITY"]
            item["views"] = body_item["TS_VIEWS"]
            item["shop_url"] = body_item["TS_SHOP_URL"]
            item["publish_dept"] = body_item["TS_PUBLISH_DEPT"]
            item["pk_code"] = body_item["$PK_CODE$"]
            item["prod_type"] = search_params["fcTypeCode"]
            fetch_counts += 1
            # replace id in detail url
            yield scrapy.Request(url=self.detail_url.format(item["inner_id"]),
                                 headers={'User-Agent': USER_AGENT,
                                          'Cookie': 'JSESSIONID=' + response.meta['session_id']},
                                 callback=self.parse_detail,
                                 meta={'item': item})

        # fetch more
        if hasMore:
            # next page
            next_page = int(search_params["pageNum"]) + 1
            search_params["pageNum"] = str(next_page)
            response.meta["search_params"] = search_params
            self.logger.info(f"fetching page {next_page}, fetching counts:{fetch_counts}")
            yield scrapy.FormRequest(url=self.search_url,
                                     headers={'User-Agent': USER_AGENT,
                                              'Cookie': 'JSESSIONID=' + response.meta['session_id']},
                                     formdata=search_params,
                                     callback=self.parse_search,
                                     meta={'search_params': search_params,
                                           'session_id': response.meta['session_id'],
                                           'fetch_counts': fetch_counts})
        else:
            self.logger.info(f"fetching {fetch_counts} standards")
            self.logger.info(f"total {counts} standards")
            self.logger.info("search done")

    def parse_detail(self, response):
        item = response.meta["item"]
        item["current_standards"] = self.extract_standard(response, "现行标准")
        item["temporary_standards"] = self.extract_standard(response, "代替标准")
        #  如果抽取到标准，记录日志
        if item["current_standards"] or item["temporary_standards"]:
            self.logger.info(f"extract valid current_standards:{item['current_standards']}")
            self.logger.info(f"extract valid temporary_standards:{item['temporary_standards']}")
        yield item
