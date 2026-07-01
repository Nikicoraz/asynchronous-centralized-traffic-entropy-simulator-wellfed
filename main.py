import asyncio
import os
from enum import Enum

import requests as req
import uvicorn
from fastapi import FastAPI
from fastapi.param_functions import Form
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

FRONTEND_URL = os.environ.get(key="FRONTEND_URL", default="http://localhost:5173")
BACKEND_URL = os.environ.get(key="BACKEND_URL", default="http://localhost:8000/api/v1")

app = FastAPI()
app.mount("/html", StaticFiles(directory="html", html=True), name="html")


class ReqTarget(Enum):
    BACKEND = BACKEND_URL
    FRONTEND = FRONTEND_URL


class ReqType(Enum):
    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4


def strTargetToEnum(target: str) -> ReqTarget:
    if target == "frontend":
        return ReqTarget.FRONTEND
    elif target == "backend":
        return ReqTarget.BACKEND

    raise ModuleNotFoundError


# Funzione generica per fare richieste con parametri comuni come jwt e payload per POST ecc...
async def makeRequest(
    type: ReqType, target_url: ReqTarget, path: str, jwt: str = "", payload={}
) -> req.Response:
    headers = {}

    if jwt:
        headers["Authorization"] = f"Bearer {jwt}"

    finalUrl = f"{target_url.value}{path}"

    if type == ReqType.GET:
        return req.get(finalUrl, headers=headers)

    raise NotImplementedError("Request type not yet implemented")


@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("html/index.html")


@app.post("/instant_requests")
async def instant(
    requests: int = Form(), jwt: str = Form(), url: str = Form(), target: str = Form()
):
    try:
        for __ in range(0, requests):
            _ = asyncio.ensure_future(
                makeRequest(ReqType.GET, strTargetToEnum(target), url, jwt=jwt)
            )

            # Decommentare le linee seguenti per vedere il codice di stato e il codice html della risposta
            # response = await _
            # print(response.status_code)
            # print(response.request.headers)
            # print(response.text)

    except Exception as e:
        print(e)
        return f"Cannot connect to URL: {e}"
    return "Requests queued"


@app.post("/sustained_requests")
async def sustained(
    requests: int = Form(),
    duration: int = Form(),
    jwt: str = Form(),
    url: str = Form(),
    target: str = Form(),
):
    try:

        async def send_requests():
            for _ in range(0, duration):
                for __ in range(0, requests):
                    ___ = asyncio.ensure_future(
                        makeRequest(ReqType.GET, strTargetToEnum(target), url, jwt=jwt)
                    )

                    # response = await ___
                    # print(response.status_code)

                await asyncio.sleep(1)

        # Esegui l'invio delle richieste in modo asincrono per dare la risposta al browser
        asyncio.get_event_loop().create_task(send_requests())
    except Exception as e:
        print(e)
        return f"Error: {e}"
    return "Requests queued"


if __name__ == "__main__":
    PORT = int(os.environ.get(key="SIM_PORT", default=8050))
    reload = False
    if bool(os.environ.get("DEBUG", False)):
        reload = True
    uvicorn.run("main:app", port=PORT, reload=reload)
