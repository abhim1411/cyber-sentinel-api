from fastapi import FastAPI, Query, UploadFile, File
import uvicorn
import os
from datetime import datetime

app = FastAPI()
# History store karne ke liye list
incident_history = []

@app.get("/status")
async def get_latest():
    return incident_history[0] if incident_history else {"status": "NOMINAL", "user": "SECURE", "timestamp": "N/A"}

@app.get("/history")
async def get_history():
    return incident_history[:20]

@app.post("/report")
async def report_incident(
    status: str = Query(...), 
    user: str = Query(...), 
    gps: str = Query(...),
    photo: UploadFile = File(None)
):
    new_alert = {
        "status": status,
        "user": user,
        "gps": gps,
        "timestamp": datetime.now().strftime("%H:%M:%S | %d %b"),
        "id": os.urandom(3).hex() 
    }
    incident_history.insert(0, new_alert)
    return {"res": "SYNC_SUCCESS"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)