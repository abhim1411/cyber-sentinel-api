from fastapi import FastAPI, Query, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import uvicorn
import os
import shutil
from datetime import datetime

app = FastAPI()

# Photos save karne ke liye folder
UPLOAD_DIR = "captured_photos"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

incident_history = []

@app.get("/status")
async def get_latest():
    return incident_history[0] if incident_history else {"status": "NOMINAL", "user": "SECURE", "timestamp": "N/A"}

@app.get("/history")
async def get_history():
    return incident_history[:20]

# --- IMAGE DOWNLOAD ENDPOINT (Mobile App ke liye) ---
@app.get("/download_photo/{incident_id}")
async def download_photo(incident_id: str):
    file_path = os.path.join(UPLOAD_DIR, f"{incident_id}.jpg")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    # Agar photo nahi milti toh default error
    raise HTTPException(status_code=404, detail="Photo not found")

@app.post("/report")
async def report_incident(
    status: str = Query(...), 
    user: str = Query(...), 
    gps: str = Query(...),
    photo: UploadFile = File(None)
):
    incident_id = os.urandom(3).hex()
    
    # Image ko save karne ka logic
    if photo:
        file_path = os.path.join(UPLOAD_DIR, f"{incident_id}.jpg")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

    new_alert = {
        "status": status,
        "user": user,
        "gps": gps,
        "timestamp": datetime.now().strftime("%H:%M:%S | %d %b"),
        "id": incident_id 
    }
    incident_history.insert(0, new_alert)
    return {"res": "SYNC_SUCCESS", "id": incident_id}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)