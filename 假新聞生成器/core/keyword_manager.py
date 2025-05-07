

import logging
import random
from db.repository import KeywordRepository

logger = logging.getLogger(__name__)

class KeywordManager:
    """管理標題生成所需的關鍵詞"""
    
    def __init__(self, repository=None):
        """初始化關鍵詞管理器"""
        self.repository = repository or KeywordRepository()
    
    def get_random_keyword(self, category):
        """獲取指定類別的隨機關鍵詞"""
        keywords = self.repository.get_keywords_by_category(category)
        
        if not keywords or not keywords.get("words", []):
            logger.warning(f"類別 '{category}' 未找到關鍵詞或為空")
            return f"[{category}]"  # 如果沒有關鍵詞，返回類別名做為佔位符
        
        return random.choice(keywords["words"])
    
    def add_keyword(self, category, word):
        """向指定類別添加新關鍵詞"""
        return self.repository.add_keyword(category, word)
    
    def add_keywords_batch(self, category, words):
        """批量添加關鍵詞"""
        return self.repository.add_keywords_batch(category, words)
    
    def ensure_keywords_exist(self):
        """確保系統中有基本關鍵詞"""
        count = self.repository.count_keyword_categories()
        
        # 如果沒有關鍵詞，載入基本關鍵詞
        if count == 0:
            logger.info("沒有發現關鍵詞，正在載入默認關鍵詞...")
            self._load_default_keywords()
            logger.info("默認關鍵詞載入完成")
        
        return self.repository.count_keyword_categories()
    
    def _load_default_keywords(self):
        """載入默認關鍵詞"""
        keyword_categories = {
            "人物": ["政府高官", "知名企業家", "國際明星", "資深記者", "著名科學家", 
                    "反對派領導人", "神秘富豪", "退休將軍"],
            "動作": ["簽署秘密協議", "洩露機密文件", "捐贈巨額資金", "突然辭職", 
                    "私下會晤", "公開批評", "隱瞞真相", "秘密調查"],
            "結果": ["引發全國關注", "導致股市崩盤", "激起民眾抗議", "促使政府干預", 
                    "引起國際譴責", "造成嚴重後果", "震驚政界"],
            # ... 更多默認關鍵詞 ...
        }
        
        for category, words in keyword_categories.items():
            self.repository.save_keyword_category(category, words)