from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field
from robot.speech import tts

router=APIRouter(prefix="/speech",tags=["speech"])
class LanguageRequest(BaseModel):language:str
class VoiceRequest(BaseModel):language:str;voice:str
class SayRequest(BaseModel):
    text:str=Field(min_length=1,max_length=500)
    language:str|None=None

@router.get("/settings")
def get_settings():return tts.status()

@router.post("/language")
def set_language(value:LanguageRequest):
    try:tts.set_language(value.language);return tts.status()
    except ValueError as error:raise HTTPException(status_code=400,detail=str(error)) from error

@router.post("/voice")
def set_voice(value:VoiceRequest):
    try:return tts.set_voice(value.language,value.voice)
    except ValueError as error:raise HTTPException(status_code=400,detail=str(error)) from error

@router.post("/say")
def say(value:SayRequest):
    try:return tts.say(value.text,language=value.language)
    except ValueError as error:raise HTTPException(status_code=400,detail=str(error)) from error
    except Exception as error:raise HTTPException(status_code=503,detail=str(error)) from error

class TuningRequest(BaseModel):
    pitch:float
    speed:float

@router.post("/tuning")
def set_tuning(value:TuningRequest):
    try:return tts.set_tuning(value.pitch,value.speed)
    except ValueError as error:raise HTTPException(status_code=400,detail=str(error)) from error
