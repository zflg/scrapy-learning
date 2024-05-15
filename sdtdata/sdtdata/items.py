# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SdtdataItem(scrapy.Item):
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
    inner_id = scrapy.Field()
    no = scrapy.Field()
    table_code = scrapy.Field()
    name = scrapy.Field()
    release_date = scrapy.Field()
    implement_date = scrapy.Field()
    has_file = scrapy.Field()
    is_validity = scrapy.Field()
    views = scrapy.Field()
    shop_url = scrapy.Field()
    publish_dept = scrapy.Field()
    pk_code = scrapy.Field()
    current_standards = scrapy.Field()
    temporary_standards = scrapy.Field()
    prod_type = scrapy.Field()
