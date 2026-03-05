from fastapi import FastAPI, Form, UploadFile, File
import uvicorn
import os

app = FastAPI()
latest_alert = {}

@app.get("/status")
async def get_status():
    return latest_alert

@app.post("/report")
async def report_incident(status: str = Form(...), user: str = Form(...), gps: str = Form(...)):
    global latest_alert
    latest_alert = {"status": status, "user": user, "gps": gps, "timestamp": os.urandom(4).hex()}
    return {"res": "Synced"}

if __name__ == "__main__":
    # Render uses a dynamic PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)