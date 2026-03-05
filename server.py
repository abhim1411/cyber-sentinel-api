from fastapi import FastAPI, Query, UploadFile, File
import os
from typing import Optional

app = FastAPI()
latest_alert = {}

@app.get("/status")
async def get_status():
    return latest_alert

@app.post("/report")
async def report_incident(
    status: str = Query(...), 
    user: str = Query(...), 
    gps: str = Query(...),
    photo: Optional[UploadFile] = File(None)
):
    global latest_alert
    latest_alert = {
        "status": status,
        "user": user,
        "gps": gps,
        "timestamp": os.urandom(3).hex() # Flutter ko change detect karne mein help karega
    }
    return {"res": "Success"}