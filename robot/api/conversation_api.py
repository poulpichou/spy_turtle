from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field
from robot.brain import conversation
from robot.speech import tts

router=APIRouter(prefix="/conversation",tags=["conversation"])
class AskRequest(BaseModel):
    text:str=Field(min_length=1,max_length=500)
    language:str|None=None

@router.post("/ask")
def ask(value:AskRequest):
    try:
        result=conversation.ask(value.text,value.language)
        speech=tts.say(result["answer"],language=result["language"])
        return {"ok":True,**result,"spoken":speech["ok"]}
    except ValueError as error:raise HTTPException(status_code=400,detail=str(error)) from error
    except RuntimeError as error:raise HTTPException(status_code=503,detail=str(error)) from error

@router.post("/reset")
def reset():conversation.reset();return {"ok":True}
