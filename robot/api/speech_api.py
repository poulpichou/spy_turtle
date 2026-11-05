from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field
from robot.speech import tts

router=APIRouter(prefix="/speech",tags=["speech"])

class LanguageRequest(BaseModel):language:str
class SayRequest(BaseModel):text:str=Field(min_length=1,max_length=500)

@router.get("/settings")
def get_settings():return tts.status()

@router.post("/language")
def set_language(value:LanguageRequest):
    try:tts.set_language(value.language);return tts.status()
    except ValueError as error:raise HTTPException(status_code=400,detail=str(error)) from error

@router.post("/say")
def say(value:SayRequest):
    try:return tts.say(value.text)
    except ValueError as error:raise HTTPException(status_code=400,detail=str(error)) from error
    except Exception as error:raise HTTPException(status_code=503,detail=str(error)) from error
