# uvicorn main:app --reload --port 8080
# ngrok http 8080 --domain singular-swine-deeply.ngrok-free.app
# ngrok http --url=singular-swine-deeply.ngrok-free.app 80

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont
from googletrans import Translator
import base64
import logging
import time

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
 
from Image_Generator.image_generator import generate_image
from io import BytesIO
import asyncio

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

BASE_DIR = "./BASE_DIR"
os.makedirs(BASE_DIR, exist_ok=True)

@app.get("/")
def root_index():
    return {"messages": "서버 가동 중"}

class GenerateRequest(BaseModel):
    prompt: str
    description: str

class GenerateResponse(BaseModel):
    image: str

async def async_generate_image(prompt: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generate_image, prompt)

def translate_to_english(text: str) -> str:
    translator = Translator()
    translation = translator.translate(text, dest='en')
    return f"{translation.text}, sharp focus, 3D style"

def add_text_to_image(image, description_text):
    try:
        background_ticket = Image.open("font_bg/bg.png")
        text_ticket = Image.open("font_bg/txtbg.png")
        
        font = ImageFont.truetype("font_bg/SCDream3.otf", 65)
        
        text_ticket_img = ImageDraw.Draw(text_ticket)
        
        line_spacing = 20
        y_text = 30
        
        lines = description_text.split('\n')
        
        for line in lines:
            bbox = font.getbbox(line)
            text_ticket_img.text(
                (30, y_text),
                line,
                font=font,
                fill=(0, 0, 0)
            )
            y_text += bbox[3] + line_spacing
        
        background_ticket.paste(image, (30, 30))
        background_ticket.paste(text_ticket, (1360, 30))
        background_ticket.save("BASE_DIR/ticket.png", format="PNG")
        
        return background_ticket
    except Exception as e:
        logger.error(f"텍스트 추가 중 오류 발생: {str(e)}")
        raise

@app.post("/generate-image", response_model=GenerateResponse)
async def generate_image_endpoint(request: GenerateRequest):
    start_time = time.time()
    logger.info(f"이미지 생성 요청 받음: {request.prompt}")
    
    try:
        logger.info("영어로 번역 시작")
        english_prompt = translate_to_english(request.prompt)
        logger.info(f"번역 완료: {english_prompt}")

        logger.info("이미지 생성 시작")
        initial_buffer = await async_generate_image(english_prompt)
        logger.info("이미지 생성 완료")
        
        logger.info("이미지에 텍스트 추가 시작")
        image = Image.open(initial_buffer)
        final_image = add_text_to_image(image, request.description)
        logger.info("이미지에 텍스트 추가 완료")
        
        logger.info("이미지를 base64로 인코딩 시작")
        buffered = BytesIO()
        final_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        logger.info("이미지를 base64로 인코딩 완료")
        
        end_time = time.time()
        logger.info(f"총 처리 시간: {end_time - start_time:.2f}초")
        
        logger.info("이미지 전송 시작")
        return JSONResponse(content={"image": img_str})
    
    except Exception as e:
        logger.error(f"이미지 생성 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))