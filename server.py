from fastapi import FastAPI, Query, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import shutil
from datetime import datetime

app = FastAPI()

# --- CORS SETTINGS (Zaroori taaki Flutter App connect ho sake) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Production mein ise restricted rakha jata hai
    allow_methods=["*"],
    allow_headers=["*"],
)

# Photos save karne ke liye folder
UPLOAD_DIR = "captured_photos"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Global variables (In-memory storage)
incident_history = []
lock_state = {"lock_active": False}

@app.get("/")
async def root():
    return {"status": "Cyber-Sentinel C2 Online", "timestamp": datetime.now().isoformat()}

@app.get("/status")
async def get_latest():
    return incident_history[0] if incident_history else {"status": "NOMINAL", "user": "SECURE", "timestamp": "N/A"}

@app.get("/history")
async def get_history():
    return incident_history[:20]

# --- IMAGE DOWNLOAD ---
@app.get("/download_photo/{incident_id}")
async def download_photo(incident_id: str):
    file_path = os.path.join(UPLOAD_DIR, f"{incident_id}.jpg")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Incident photo not found")

# --- REMOTE LOCKDOWN LOGIC ---

@app.post("/lock-system")
async def trigger_lock():
    global lock_state
    lock_state["lock_active"] = True
    print(f"[!] ALERT: Remote Lock Command Issued at {datetime.now()}")
    return {"status": "success", "lock_active": True}

@app.get("/get_lock_status")
async def get_lock_status():
    return lock_state

@app.get("/reset_lock")
async def reset_lock():
    global lock_state
    lock_state["lock_active"] = False
    print("[+] System Status: Unlocked/Normal")
    return {"status": "success", "lock_active": False}

# --- INCIDENT REPORTING ---
@app.post("/report")
async def report_incident(
    status: str = Query(...), 
    user: str = Query(...), 
    gps: str = Query(...),
    photo: UploadFile = File(None)
):
    incident_id = os.urandom(3).hex()
    
    if photo:
        file_path = os.path.join(UPLOAD_DIR, f"{incident_id}.jpg")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

    new_alert = {
        "id": incident_id,
        "status": status,
        "user": user,
        "gps": gps,
        "timestamp": datetime.now().strftime("%H:%M:%S | %d %b"),
    }
    
    incident_history.insert(0, new_alert)
    return {"res": "SYNC_SUCCESS", "id": incident_id}

@app.post("/acknowledge/{incident_id}")
async def acknowledge_incident(incident_id: str):
    print(f"[ACK] Incident {incident_id} verified by Operator.")
    return {"res": "ACK_SUCCESS"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(app, host="0.0.0.0", port=port)
