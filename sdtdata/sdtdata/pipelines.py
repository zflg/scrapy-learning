# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json

# useful for handling different item types with a single interface
import pymysql
from scrapy.exceptions import DropItem
from sdtdata import settings


class SdtdataPipeline:
    def __init__(self):
        self.connection = pymysql.connect(
            host=settings.MYSQL_HOST,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            db=settings.MYSQL_DATABASE,
            port=settings.MYSQL_PORT,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        try:
            # check if item exists
            self.cursor.execute("SELECT * FROM `sdtdata` WHERE `inner_id` = %s", item["inner_id"])
            exist = self.cursor.fetchone()
            if exist:
                # prod types 是一个以|分割的字符串
                prod_types = exist["prod_types"]
                spider.logger.info(f"prod_types: {prod_types}")
                if prod_types is None or prod_types == "":
                    sql = "UPDATE `sdtdata` SET `prod_types` = %s WHERE `inner_id` = %s"
                    self.cursor.execute(sql, (f"{item['prod_type']}", item["inner_id"]))
                elif item["prod_type"] not in prod_types.split("|"):
                    sql = "UPDATE `sdtdata` SET `prod_types` = %s WHERE `inner_id` = %s"
                    self.cursor.execute(sql, (f"{prod_types}|{item['prod_type']}", item["inner_id"]))
                self.connection.commit()
                return item
            # insert into database
            spider.logger.info(f"Inserting item {item['inner_id']} into database")
            sql = ("INSERT INTO `sdtdata` (`inner_id`,"
                   "`no`,"
                   "`table_code`,"
                   "`name`,"
                   "`release_date`,"
                   "`implement_date`,"
                   "`has_file`,"
                   "`is_validity`,"
                   "`views`,"
                   "`shop_url`,"
                   "`publish_dept`,"
                   "`pk_code`,"
                   "`current_standards`,"
                   "`temporary_standards`,"
                   "`prod_types`,"
                   "`create_time`,"
                   "`update_time`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())")
            values = (
                item["inner_id"],
                item["no"],
                item["table_code"],
                item["name"],
                # 如果是空字符串(空字符或者全是空格)，就插入None
                item["release_date"] if item["release_date"].strip() else None,
                item["implement_date"] if item["implement_date"].strip() else None,
                item["has_file"],
                item["is_validity"],
                item["views"],
                item["shop_url"],
                item["publish_dept"],
                item["pk_code"],
                json.dumps(item["current_standards"]),
                json.dumps(item["temporary_standards"]),
                item["prod_type"]
            )
            self.cursor.execute(sql, values)
            self.connection.commit()
            return item
        except Exception as e:
            spider.logger.error(f"Error saving item to database: {e}")
            raise DropItem(f"Failed to save item {item}")

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()
