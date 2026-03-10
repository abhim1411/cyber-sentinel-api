from fastapi import FastAPI, Query, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from requests import post
import uvicorn
import os
import shutil
from datetime import datetime

app = FastAPI()

# Photos save karne ke liye folder
UPLOAD_DIR = "captured_photos"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Global variables for history and lockdown state
incident_history = []
lock_state = {"lock_active": False} # Default status is False

@app.get("/status")
async def get_latest():
    return incident_history[0] if incident_history else {"status": "NOMINAL", "user": "SECURE", "timestamp": "N/A"}

@app.get("/history")
async def get_history():
    # Return latest 20 alerts
    return incident_history[:20]

# --- IMAGE DOWNLOAD ENDPOINT (Mobile App ke liye) ---
@app.get("/download_photo/{incident_id}")
async def download_photo(incident_id: str):
    file_path = os.path.join(UPLOAD_DIR, f"{incident_id}.jpg")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Photo not found")

# --- REMOTE LOCKDOWN ROUTES ---

@post("/lock-system")
async def trigger_lock():
    """Flutter App isse hit karegi lockdown activate karne ke liye"""
    global lock_state
    lock_state["lock_active"] = True
    print(f"[!] REMOTE LOCK COMMAND RECEIVED AT {datetime.now()}")
    return {"status": "success", "message": "Lock command broadcasted to agent"}

@app.get("/get_lock_status")
async def get_lock_status():
    """Python Agent (Laptop) isse hit karega check karne ke liye"""
    return lock_state

@app.post("/reset_lock")
async def reset_lock():
    """Python Agent unlock hone ke baad status reset karega"""
    global lock_state
    lock_state["lock_active"] = False
    print("[+] Lock status reset to normal (Unlocked)")
    return {"status": "success", "message": "System status reset"}

# --- INCIDENT REPORTING ENDPOINT ---
@app.post("/report")
async def report_incident(
    status: str = Query(...), 
    user: str = Query(...), 
    gps: str = Query(...),
    photo: UploadFile = File(None)
):
    incident_id = os.urandom(3).hex()
    
    # Image save logic
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
    
    # Latest alert ko top par rakhne ke liye insert at 0
    incident_history.insert(0, new_alert)
    return {"res": "SYNC_SUCCESS", "id": incident_id}

# --- ACKNOWLEDGE ALERT ---
@app.post("/acknowledge/{incident_id}")
async def acknowledge_incident(incident_id: str):
    """Mobile app se alert hatane ya log karne ke liye"""
    print(f"[+] Incident {incident_id} acknowledged by operator.")
    return {"res": "ACK_SUCCESS"}

if __name__ == "__main__":
    # Render ya local host configuration
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)