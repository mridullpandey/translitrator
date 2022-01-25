from typing import Optional
from typing_extensions import runtime
from fastapi import FastAPI,HTTPException
from fastapi.params import Body
from fastapi import FastAPI
from  app.E_to_H import Database_Search_English
# from app.H_to_E import Database_Search_Hindi
app = FastAPI()

#domain where this api is hosted for example : localhost:5000/docs to see swagger documentation automagically generated.


@app.get("/{english}")
async def translitration(english:str):
    hindi=Database_Search_English(english)
    if not hindi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"I'm sorry {id} can't be translitrated")

    return{'Hindi': hindi}
