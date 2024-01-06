import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from server.routes import main_services

import warnings
import uvicorn
import dotenv

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d %B %Y %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            filename='./logs/AbstractSumarization.log',
            mode='a'
        )
    ],
)

logger = logging.getLogger('')
logger.propagate = False

if '.env' in os.listdir():
    dotenv.load_dotenv('.env')

warnings.filterwarnings("ignore")

app = FastAPI(
    title=f"Abstract Summarization API - DEMO",
    redoc_url=False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(main_services.router)

logger.info(f"HOST: {os.getenv('HOST','0.0.0.0')}:{os.getenv('PORT','1111')}")

@app.get('/')
def ping():
    logger.info("Received request")
    return {'message': 'Abstract Summarization API'}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"message": "ERROR BAD REQUEST"},
    )

if __name__ == '__main__':
    uvicorn.run("app:app",
                port=int(os.getenv('PORT', '1111')),
                host=os.getenv('HOST', '0.0.0.0'),
                reload=eval(os.getenv("DEBUG", 'True')),
                workers=int(os.getenv('WORKER', 1))
                )
