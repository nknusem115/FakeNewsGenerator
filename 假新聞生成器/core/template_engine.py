#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模板處理系統 - 負責管理、選擇和填充假新聞標題模板
"""

import re
import json
import random
import os
from typing import Dict, List, Tuple, Any, Set
import logging

from .keyword_manager import KeywordManager

logger = logging.getLogger('headline_generator.template')


class TemplateEngine:
    """標題模板引擎"""
    
    def __init__(self, templates_file: str = None):
        """
        初始化模板引擎
        
        Args:
            templates_file: 模板文件路徑（如果未提供，將使用默認模板）
        """
        self.templates = []  # 格式：[{"template": "...", "category": "..."}, ...]
        self.placeholder_pattern = re.compile(r'\[(.*?)\]')
        
        if templates_file and os.path.exists(templates_file):
            self.load_templates_from_file(templates_file)
    
    def load_templates_from_file(self, file_path: str) -> None:
        """
        從文件載入模板
        
        Args:
            file_path: 模板文件路徑
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.templates = json.load(f)
            logger.info(f"從 {file_path} 載入了 {len(self.templates)} 個模板")
        except Exception as e:
            logger.error(f"載入模板文件時出錯: {str(e)}")
            # 載入失敗時使用默認模板
            self.load_default_templates()
    
    def load_templates(self, templates: List[Dict]) -> None:
        """
        載入模板列表
        
        Args:
            templates: 模板列表
        """
        self.templates = templates
        logger.info(f"載入了 {len(self.templates)} 個模板")
    
    def load_default_templates(self) -> None:
        """載入默認模板"""
        self.templates = [
            # 政治類
            {"template": "[人物]宣布[動作]，[結果]引發爭議", "category": "政治"},
            {"template": "[人物][時間][地點][動作]，[機構]表示將[反應]", "category": "政治"},
            {"template": "獨家：[人物]被發現秘密[動作]，[機構]緊急[反應]", "category": "政治"},
            {"template": "[人物]：[數字]%的[人群][觀點]，[結果]需要重視", "category": "政治"},
            {"template": "[機構]發布[政策]，專家：將[結果]", "category": "政治"},
            {"template": "[地點][事件]後，[人物]緊急[動作]，引發[結果]", "category": "政治"},
            
            # 社會類
            {"template": "震驚！[地點][數字]名[人群][動作]，[結果]", "category": "社會"},
            {"template": "[地點]發生[事件]，目擊者：「[描述]」", "category": "社會"},
            {"template": "最新報導：[地點][事件]造成[數字]人[結果]", "category": "社會"},
            {"template": "[地點][機構]公布[數字]項[政策]，專家：[觀點]", "category": "社會"},
            {"template": "調查顯示：[數字]%[地點][人群][觀點]", "category": "社會"},
            
            # 經濟類
            {"template": "[行業]巨頭[公司][動作]，[行業]股價[結果]", "category": "經濟"},
            {"template": "[公司]宣布[數字]億元[動作]，[行業]將迎來[結果]", "category": "經濟"},
            {"template": "突發：[地點][行業]市場[結果]，[機構]緊急[反應]", "category": "經濟"},
            {"template": "[人物]：[時間]內[行業]將迎來[事件]", "category": "經濟"},
            {"template": "分析師預測：[行業][時間]內[結果]，[公司]將[反應]", "category": "經濟"},
            
            # 科技類
            {"template": "[公司]發布革命性[產品]，[行業]專家：將[結果]", "category": "科技"},
            {"template": "突破：[機構]科學家[動作]，有望解決[問題]", "category": "科技"},
            {"template": "[數字]%[行業]專家警告：[事件]將在[時間]內發生", "category": "科技"},
            {"template": "[人物]宣布[產品]將在[時間][動作]，[行業]震動", "category": "科技"},
            {"template": "研究發現：[技術]可能[結果]，[機構]呼籲[反應]", "category": "科技"},
            
            # 國際類
            {"template": "[國家]宣布[動作]，[國家]外交部：將[反應]", "category": "國際"},
            {"template": "[國家][事件]後，[國家]緊急[動作]", "category": "國際"},
            {"template": "[國際組織]：[國家][動作]將導致[結果]", "category": "國際"},
            {"template": "[國家][人物]訪問[國家]，雙方同意[動作]", "category": "國際"},
            {"template": "[國家]發生[事件]，[數字]國表示[反應]", "category": "國際"},
            
            # 健康類
            {"template": "研究：每天[動作]可降低[數字]%[疾病]風險", "category": "健康"},
            {"template": "專家警告：[食物]可能導致[疾病]，建議[反應]", "category": "健康"},
            {"template": "新研究顯示：[習慣]與[疾病]有直接關聯", "category": "健康"},
            {"template": "[機構]發現：[數字]%的[人群]缺乏[營養]，可能導致[結果]", "category": "健康"},
            {"template": "[地點]爆發[疾病]，專家建議民眾[反應]", "category": "健康"},
            
            # 教育類
            {"template": "[機構]最新研究：[教育方式]可提高學生[能力][數字]%", "category": "教育"},
            {"template": "[地點]教育廳宣布：將在[時間]內[動作]", "category": "教育"},
            {"template": "調查：[數字]%的家長認為[教育觀點]", "category": "教育"},
            {"template": "[人物]倡導[教育方式]，專家：將[結果]", "category": "教育"},
            {"template": "[機構]發布[數字]項教育改革措施，學生家長[反應]", "category": "教育"},
            
            # 娛樂類
            {"template": "獨家：[明星]被爆[動作]，經紀公司[反應]", "category": "娛樂"},
            {"template": "[明星]宣布[動作]，粉絲：「[描述]」", "category": "娛樂"},
            {"template": "爆料：[明星]與[明星]疑似[關係]，[時間]後官宣", "category": "娛樂"},
            {"template": "[明星]新[作品]銷量突破[數字]，創造[行業]新紀錄", "category": "娛樂"},
            {"template": "內部消息：[明星]因[原因][動作]，[結果]", "category": "娛樂"},
        ]
        logger.info(f"已載入 {len(self.templates)} 個默認模板")
    
    def get_all_templates(self) -> List[Dict]:
        """
        獲取所有模板
        
        Returns:
            List[Dict]: 模板列表
        """
        return self.templates
    
    def count_templates(self) -> int:
        """
        獲取模板數量
        
        Returns:
            int: 模板數量
        """
        return len(self.templates)
    
    def get_random_template(self) -> Tuple[str, str]:
        """
        隨機選擇一個模板
        
        Returns:
            Tuple[str, str]: (模板文本, 類別)
        """
        if not self.templates:
            raise ValueError("沒有可用的模板")
        
        template_info = random.choice(self.templates)
        return template_info["template"], template_info["category"]
    
    def get_template_by_category(self, category: str) -> Tuple[str, str]:
        """
        根據類別獲取模板
        
        Args:
            category: 新聞類別
            
        Returns:
            Tuple[str, str]: (模板文本, 類別)
        """
        category_templates = [t for t in self.templates if t["category"] == category]
        if not category_templates:
            logger.warning(f"未找到類別為 '{category}' 的模板，使用隨機模板")
            return self.get_random_template()
        
        template_info = random.choice(category_templates)
        return template_info["template"], template_info["category"]
    
    def extract_placeholders(self, template: str) -> List[str]:
        """
        從模板中提取所有佔位符
        
        Args:
            template: 模板字符串
            
        Returns:
            List[str]: 佔位符列表
        """
        matches = self.placeholder_pattern.findall(template)
        return matches
    
    def fill_template(self, template: str, keyword_manager: KeywordManager) -> Tuple[str, Dict[str, str]]:
        """
        填充模板中的關鍵詞佔位符
        
        Args:
            template: 模板字符串
            keyword_manager: 關鍵詞管理器
            
        Returns:
            Tuple[str, Dict[str, str]]: (填充後的標題, 使用的關鍵詞字典)
        """
        placeholders = self.extract_placeholders(template)
        filled_template = template
        used_keywords = {}
        
        # 避免重複使用相同關鍵詞的記錄
        used_words = set()
        
        for placeholder in placeholders:
            # 獲取適當的關鍵詞
            keyword = keyword_manager.get_keyword(placeholder, exclude=used_words)
            
            # 如果找不到關鍵詞，使用佔位符本身
            if not keyword:
                keyword = f"某{placeholder}"
            
            # 記錄使用的關鍵詞並替換模板
            used_keywords[placeholder] = keyword
            filled_template = filled_template.replace(f"[{placeholder}]", keyword, 1)
            used_words.add(keyword)
        
        return filled_template, used_keywords
    
    def add_template(self, template: str, category: str) -> None:
        """
        添加新模板
        
        Args:
            template: 模板字符串
            category: 類別
        """
        self.templates.append({
            "template": template,
            "category": category
        })
        logger.info(f"已添加新模板: '{template}' (類別: {category})")
    
    def save_templates_to_file(self, file_path: str) -> None:
        """
        保存模板到文件
        
        Args:
            file_path: 文件路徑
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)
            logger.info(f"已將 {len(self.templates)} 個模板保存到 {file_path}")
        except Exception as e:
            logger.error(f"保存模板文件時出錯: {str(e)}")


if __name__ == "__main__":
    # 簡單測試
    from keyword_manager import KeywordManager
    
    logging.basicConfig(level=logging.INFO)
    
    engine = TemplateEngine()
    engine.load_default_templates()
    
    km = KeywordManager()
    km.load_default_keywords()
    
    # 測試填充模板
    template, category = engine.get_random_template()
    print(f"模板: {template}")
    print(f"類別: {category}")
    
    headline, keywords = engine.fill_template(template, km)
    print(f"生成標題: {headline}")
    print(f"使用的關鍵詞: {keywords}")