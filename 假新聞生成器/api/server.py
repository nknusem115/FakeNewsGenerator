import logging
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from core.generator import HeadlineGenerator
from utils.metrics import track_api_usage

logger = logging.getLogger(__name__)

# 建立FastAPI應用
app = FastAPI(
    title="假新聞標題生成器API",
    description="生成和管理假新聞標題的API服務",
    version="1.0.0"
)

# 添加CORS中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 請求模型
class GenerateRequest(BaseModel):
    count: int = Field(1, description="要生成的標題數量", ge=1, le=1000)
    category: Optional[str] = Field(None, description="標題類別(如政治,科技)")
    enhance: bool = Field(False, description="是否使用語言模型增強")

class SearchRequest(BaseModel):
    query: str = Field(..., description="搜索關鍵詞")
    limit: int = Field(20, description="最大結果數", ge=1, le=100)

# 回應模型
class HeadlineResponse(BaseModel):
    headline: str
    category: str
    created_at: str
    keywords_used: Optional[Dict[str, str]] = None

class GenerateResponse(BaseModel):
    success: bool
    count: int
    headlines: List[HeadlineResponse]
    execution_time: float

# 依賴項
def get_generator():
    return HeadlineGenerator()

# 路由
@app.post("/generate", response_model=GenerateResponse)
async def generate_headlines(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    generator: HeadlineGenerator = Depends(get_generator)
):
    """生成假新聞標題"""
    import time
    start_time = time.time()
    
    try:
        results = generator.generate_headlines_batch(
            count=request.count,
            enhance_ratio=0.3 if request.enhance else 0
        )
        
        # 處理回應格式
        headlines = []
        for result in results:
            headlines.append({
                "headline": result["headline"],
                "category": result["category"],
                "created_at": result["created_at"].isoformat(),
                "keywords_used": result.get("keywords_used")
            })
        
        execution_time = time.time() - start_time
        
        # 非阻塞地跟踪API使用情況
        background_tasks.add_task(
            track_api_usage,
            endpoint="generate",
            count=request.count,
            execution_time=execution_time
        )
        
        return {
            "success": True,
            "count": len(headlines),
            "headlines": headlines,
            "execution_time": execution_time
        }
        
    except Exception as e:
        logger.error(f"生成標題時發生錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成標題失敗: {str(e)}")

# ... 其他API路由 ...

# 啟動服務
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)