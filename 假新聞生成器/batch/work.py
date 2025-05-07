import time
import logging
import multiprocessing
from config.settings import WORKER_CONFIG
from core.generator import HeadlineGenerator

logger = logging.getLogger(__name__)

class GenerationWorker:
    """標題生成工作者"""
    
    def __init__(self, config=None):
        """初始化工作者"""
        self.config = config or WORKER_CONFIG
        self.generator = HeadlineGenerator()
        self.batch_size = self.config.get("batch_size", 1000)
        self.running = False
    
    def start(self):
        """啟動工作者進程"""
        if self.running:
            logger.warning("工作者已在運行中")
            return False
        
        self.running = True
        logger.info("正在啟動工作者進程...")
        
        # 創建子進程
        self.process = multiprocessing.Process(
            target=self._work_loop,
            args=()
        )
        self.process.daemon = True
        self.process.start()
        
        logger.info(f"工作者進程已啟動 (PID: {self.process.pid})")
        return True
    
    def stop(self):
        """停止工作者進程"""
        if not self.running:
            logger.warning("工作者未運行")
            return False
        
        logger.info("正在停止工作者進程...")
        self.running = False
        
        # 給進程一些時間優雅地退出
        timeout = 5
        self.process.join(timeout)
        
        # 如果進程仍在運行，強制終止
        if self.process.is_alive():
            logger.warning(f"工作者進程未在{timeout}秒內退出，正在強制終止")
            self.process.terminate()
            self.process.join()
        
        logger.info("工作者進程已停止")
        return True
    
    def _work_loop(self):
        """工作循環"""
        logger.info("工作者循環已啟動")
        
        while self.running:
            try:
                # 從任務隊列獲取任務
                task = self._get_next_task()
                
                if task:
                    self._process_task(task)
                else:
                    # 沒有任務，休息一下
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"工作循環中出現錯誤: {str(e)}")