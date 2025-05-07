

import logging
import requests
import time
from config.settings import LANGUAGE_MODEL_CONFIG

logger = logging.getLogger(__name__)

class LanguageModelService:
    """整合外部語言模型API的服務"""
    
    def __init__(self, config=None):
        """初始化語言模型服務"""
        self.config = config or LANGUAGE_MODEL_CONFIG
        self.enabled = self.config.get("enabled", False)
        self.api_url = self.config.get("api_url", "")
        self.api_key = self.config.get("api_key", "")
        self.max_retries = self.config.get("max_retries", 3)
        self.retry_delay = self.config.get("retry_delay", 1)
    
    def is_available(self):
        """檢查語言模型服務是否可用"""
        return self.enabled and self.api_url and self.api_key
    
    def enhance_headline(self, headline):
        """使用語言模型增強標題"""
        if not self.is_available():
            logger.warning("語言模型服務未啟用或配置不完整")
            return headline
        
        retries = 0
        while retries < self.max_retries:
            try:
                payload = {
                    "prompt": f"增強以下假新聞標題的可信度和吸引力，但保持相同的主題：\n{headline}",
                    "max_tokens": 50,
                    "temperature": 0.7
                }
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                response = requests.post(
                    self.api_url, 
                    json=payload, 
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    enhanced_headline = result.get("choices", [{}])[0].get("text", "").strip()
                    
                    if enhanced_headline:
                        logger.debug(f"標題增強成功: '{headline}' -> '{enhanced_headline}'")
                        return enhanced_headline
                    else:
                        logger.warning("API返回空標題")
                        return headline
                
                # 處理API錯誤
                logger.error(f"API請求失敗: {response.status_code}, {response.text}")
                
                # 如果是速率限制錯誤，等待後重試
                if response.status_code == 429:
                    retries += 1
                    time.sleep(self.retry_delay * (2 ** retries))  # 指數退避
                    continue
                    
                return headline  # 其他錯誤直接返回原標題
                
            except Exception as e:
                logger.error(f"增強標題時發生錯誤: {str(e)}")
                retries += 1
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    return headline
        
        return headline  # 重試失敗後返回原標題
    
    def batch_enhance_headlines(self, headlines, max_concurrent=5):
        """批量增強標題"""
        if not self.is_available():
            return headlines
        
        from concurrent.futures import ThreadPoolExecutor
        
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            return list(executor.map(self.enhance_headline, headlines))