from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from telethon import TelegramClient
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()

app = FastAPI(title="Notification Service")

app.add_middleware(
   CORSMiddleware,
   allow_origins=["http://localhost:5000", "http://localhost:5001"],
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE')

client = TelegramClient('notif_erp', API_ID, API_HASH)

class MessageRequest(BaseModel):
   group_id: int
   message: str
   reply_to: Optional[int] = None

@app.post("/send")
async def send_to_telegram(request: MessageRequest):
   try:
       await client.send_message(
           entity=request.group_id,
           message=request.message,
           reply_to=request.reply_to
       )
       return {
           "message": "Successfully sent"
       }
   except Exception as e:
       raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
@app.on_event("startup") 
async def startup_event():
   await client.start(phone=PHONE)
   print("Telegram Service Ready!")

@app.on_event("shutdown")
async def shutdown_event():
   await client.disconnect()

if __name__ == "__main__":
   config = uvicorn.Config(
       app=app,
       host="0.0.0.0",
       port=5003,
       reload=False
   )
   server = uvicorn.Server(config)
   server.run()