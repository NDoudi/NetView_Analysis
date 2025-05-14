from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

app = FastAPI()

# Autoriser toutes les origines
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Définir le répertoire de stockage des fichiers téléchargés
UPLOAD_DIR = "api/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Chemin vers le fichier qui contient l'URL actuelle
TUNNEL_FILE = "api/tunnel_url.txt"  # <-- ce fichier contiendra l'URL Ngrok actuelle

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

    return JSONResponse({"status": "success", "filename": filename})

# Endpoint pour obtenir l'URL du tunnel Ngrok
@app.get("/tunnel-url")
async def get_tunnel_url():
    if os.path.exists(TUNNEL_FILE):
        with open(TUNNEL_FILE, "r") as f:
            url = f.read().strip()
        return {"url": url}
    else:
        return JSONResponse(status_code=404, content={"status": "error", "message": "Tunnel URL not found"})
