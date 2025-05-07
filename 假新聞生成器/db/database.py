import logging
from pymongo import MongoClient
from config.settings import DATABASE_CONFIG

logger = logging.getLogger(__name__)

class DatabaseManager:
    """管理資料庫連接"""
    
    _instance = None
    
    def __new__(cls):
        """單例模式實現"""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """初始化資料庫連接"""
        self.config = DATABASE_CONFIG
        self.client = None
        self.db = None
        self.connected = False
        self.connect()
    
    def connect(self):
        """連接到資料庫"""
        try:
            connection_str = self.config.get("connection_string", "mongodb://localhost:27017/")
            db_name = self.config.get("database_name", "fake_news_db")
            
            self.client = MongoClient(connection_str)
            self.db = self.client[db_name]
            self.connected = True
            
            # 驗證連接
            self.client.server_info()
            logger.info(f"成功連接到資料庫: {db_name}")
            
            return True
            
        except Exception as e:
            self.connected = False
            logger.error(f"資料庫連接失敗: {str(e)}")
            return False
    
    def get_collection(self, collection_name):
        """獲取指定的集合"""
        if not self.connected:
            if not self.connect():
                raise ConnectionError("無法連接到資料庫")
        
        return self.db[collection_name]
    
    def create_indexes(self):
        """為集合創建索引以提高性能"""
        try:
            # 為標題集合創建索引
            headlines = self.get_collection("headlines")
            headlines.create_index([("headline", "text")])  # 全文索引
            headlines.create_index("category")              # 類別索引
            headlines.create_index("created_at")            # 時間索引
            
            # 為模板集合創建索引
            templates = self.get_collection("templates")
            templates.create_index("category")
            
            # 為關鍵詞集合創建索引
            keywords = self.get_collection("keywords")
            keywords.create_index("category", unique=True)
            
            logger.info("資料庫索引創建完成")
            return True
            
        except Exception as e:
            logger.error(f"創建索引時失敗: {str(e)}")
            return False
    
    def close(self):
        """關閉資料庫連接"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("資料庫連接已關閉")