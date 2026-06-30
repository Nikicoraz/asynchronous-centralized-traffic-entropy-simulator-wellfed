import os

import requests as req
import uvicorn
from fastapi import FastAPI
from fastapi.param_functions import Form
from fastapi.responses import HTMLResponse
from fastapi.routing import FormData
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

URL = os.environ.get(key="WELLFED_URL", default="http://localhost:5173")

app = FastAPI()
app.mount("/html", StaticFiles(directory="html", html=True), name="html")


@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("html/index.html")


@app.post("/instant_requests")
async def instant(requests: int = Form(title="requests")):
    try:
        # Invia "requests" richieste all'url base, si potrebbe modificare per indicare anche un URL a cui inviare le richieste
        # oltre a che gestire i path con autenticazione ecc... Questa è solo una prova per vedere come funziona
        for i in range(0, requests):
            response = req.get(URL)

            # Decommentare le linee seguenti per vedere il codice di stato e il codice html della risposta
            # print(response.status_code)
            # print(response.text)

    except Exception as e:
        print(e)
        return "Cannot connect to URL"
    return "Requests queued"


if __name__ == "__main__":
    PORT = int(os.environ.get(key="SIM_PORT", default=8050))
    reload = False
    if bool(os.environ.get("DEBUG", False)):
        reload = True
    uvicorn.run("main:app", port=PORT, reload=reload)
