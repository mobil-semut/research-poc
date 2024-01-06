import os
import logging
import warnings
import traceback
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from ..schema import Article
from ..utils.security import get_current_user
import source.main as main

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")

router = APIRouter(tags=['Main-Services'],
                    prefix='/api/v1',
                    dependencies=[Depends(get_current_user)])

@router.post("/AbstractSummarization")
async def abstract_summarization(request_data: Article)->JSONResponse:
    try:
        resp = main.abs_summary(request_data = request_data.dict())
        return JSONResponse(resp)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        logger.error((f'sentiment analysis request fail at {datetime.now()}'))
        raise HTTPException(
            status_code=404,
            detail="Not Found"
        )
