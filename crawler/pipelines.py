# import json
# from collections import defaultdict

# from itemadapter import ItemAdapter
# from scrapy.exceptions import DropItem
# from pymongo import MongoClient


# def check_item(item):
    # adapter = ItemAdapter(item)
    # required_fields = ("url", "text", "pub_time", "views")
    # for field in required_fields:
        # value = adapter.get(field)
        # if not value:
            # raise DropItem(f"Missing {field} field in {item}")


# class MongoPipeline:
    # def open_spider(self, spider):
        # with open("configs/mongo_config.json") as r:
            # config = json.load(r)
        # self.client = MongoClient(**config["client"])
        # database_name = config["database_name"]
        # documents_collection_name = config["documents_collection_name"]
        # self.collection = self.client[database_name][documents_collection_name]

    # def process_item(self, item, spider):
        # check_item(item)
        # adapter = ItemAdapter(item)
        # url = adapter.get("url")
        # self.collection.replace_one({"url": url}, adapter.asdict(), upsert=True)
        # return item


# class JsonlPipeline:
    # def open_spider(self, spider):
        # self.items = defaultdict(dict)

    # def close_spider(self, spider):
        # with open("telegram_news.jsonl", "w") as w:
            # for _, item in self.items.items():
                # w.write(json.dumps(item, ensure_ascii=False) + "\n")

    # def process_item(self, item, spider):
        # check_item(item)
        # adapter = ItemAdapter(item)
        # url = adapter.get("url")
        # self.items[url] = adapter.asdict()
        # return item
        
import json
from collections import defaultdict
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from pymongo import ReplaceOne

def check_item(item):
    adapter = ItemAdapter(item)
    required_fields = ("url", "text", "pub_time", "views")
    for field in required_fields:
        value = adapter.get(field)
        if not value:
            raise DropItem(f"Missing {field} field in {item}")

class MongoPipeline:
    def open_spider(self, spider):
        with open("configs/mongo_config.json") as r:
            config = json.load(r)
        self.client = MongoClient(**config["client"])
        database_name = config["database_name"]
        documents_collection_name = config["documents_collection_name"]
        self.collection = self.client[database_name][documents_collection_name]
        
        # Создаём индекс один раз
        indices = self.collection.index_information()
        if "url_1" not in indices:
            self.collection.create_index([("url", 1)], name="url_1", unique=True)
        
        # Буфер для батчинга
        self.buffer = []
        self.batch_size = 200  # можно увеличить до 500-1000

    def process_item(self, item, spider):
        check_item(item)
        adapter = ItemAdapter(item)
        
        # Добавляем в буфер вместо немедленной записи
        self.buffer.append(
            ReplaceOne(
                {"url": adapter.get("url")}, 
                adapter.asdict(), 
                upsert=True
            )
        )
        
        # Когда буфер заполнился - пишем батчем
        if len(self.buffer) >= self.batch_size:
            self._flush()
        
        return item
    
    def _flush(self):
        """Записывает накопленные документы в MongoDB"""
        if not self.buffer:
            return
        
        try:
            self.collection.bulk_write(self.buffer, ordered=False)
            spider_logger = None  # можно добавить логирование
            # print(f"Wrote batch of {len(self.buffer)} items")
        except BulkWriteError as e:
            # Игнорируем ошибки дубликатов - это нормально
            pass
        
        self.buffer = []
    
    def close_spider(self, spider):
        """Записываем остатки при завершении"""
        self._flush()

class JsonlPipeline:
    def open_spider(self, spider):
        self.items = defaultdict(dict)
    
    def close_spider(self, spider):
        with open("telegram_news.jsonl", "w") as w:
            for _, item in self.items.items():
                w.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    def process_item(self, item, spider):
        check_item(item)
        adapter = ItemAdapter(item)
        url = adapter.get("url")
        self.items[url] = adapter.asdict()
        return item