import logging
from datetime import datetime
from db.database import DatabaseManager

logger = logging.getLogger(__name__)

class HeadlineRepository:
    """標題資料存取"""
    
    def __init__(self, db_manager=None):
        """初始化標題倉庫"""
        self.db_manager = db_manager or DatabaseManager()
        self.collection = self.db_manager.get_collection("headlines")
    
    def save_headline(self, headline_doc):
        """保存單個標題"""
        # 確保有創建時間
        if "created_at" not in headline_doc:
            headline_doc["created_at"] = datetime.now()
        
        result = self.collection.insert_one(headline_doc)
        headline_doc["_id"] = result.inserted_id
        return headline_doc
    
    def save_headlines_batch(self, headlines):
        """批量保存標題"""
        # 確保每個標題都有創建時間
        for headline in headlines:
            if "created_at" not in headline:
                headline["created_at"] = datetime.now()
        
        if headlines:
            result = self.collection.insert_many(headlines)
            return len(result.inserted_ids)
        return 0
    
    def find_headlines(self, query=None, limit=100, skip=0, sort_by=None):
        """查詢標題"""
        query = query or {}
        sort_by = sort_by or [("created_at", -1)]  # 默認按創建時間倒序
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort(sort_by)
        return list(cursor)
    
    def search_text(self, text, limit=20):
        """全文搜索標題"""
        query = {"$text": {"$search": text}}
        projection = {"score": {"$meta": "textScore"}}
        sort = [("score", {"$meta": "textScore"})]
        
        cursor = self.collection.find(query, projection).limit(limit).sort(sort)
        return list(cursor)
    
    def count_headlines(self, query=None):
        """計數標題數量"""
        query = query or {}
        return self.collection.count_documents(query)
    
    def delete_headline(self, headline_id):
        """刪除標題"""
        result = self.collection.delete_one({"_id": headline_id})
        return result.deleted_count
    
    def delete_headlines_by_query(self, query):
        """批量刪除標題"""
        result = self.collection.delete_many(query)
        return result.deleted_count


class TemplateRepository:
    """模板資料存取"""
    
    def __init__(self, db_manager=None):
        """初始化模板倉庫"""
        self.db_manager = db_manager or DatabaseManager()
        self.collection = self.db_manager.get_collection("templates")
    
    def save_template(self, template_doc):
        """保存模板"""
        result = self.collection.insert_one(template_doc)
        template_doc["_id"] = result.inserted_id
        return template_doc
    
    def save_templates_batch(self, templates):
        """批量保存模板"""
        if templates:
            result = self.collection.insert_many(templates)
            return len(result.inserted_ids)
        return 0
    
    def get_random_template(self, category=None):
        """獲取隨機模板"""
        match_stage = {"$match": {}} if category is None else {"$match": {"category": category}}
        sample_stage = {"$sample": {"size": 1}}
        
        pipeline = [match_stage, sample_stage]
        result = list(self.collection.aggregate(pipeline))
        
        if result:
            return result[0]
        return None
    
    def get_templates_by_category(self, category):
        """獲取指定類別的模板"""
        return list(self.collection.find({"category": category}))
    
    def count_templates(self, query=None):
        """計數模板數量"""
        query = query or {}
        return self.collection.count_documents(query)