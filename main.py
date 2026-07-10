import asyncio
import os
import time
import random
import io
import base64
import io

from enum import Enum

import requests as req
import uvicorn
from fastapi import FastAPI
from fastapi.param_functions import Form
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
from PIL import Image
from pyzbar.pyzbar import decode


FRONTEND_URL = os.environ.get(key="FRONTEND_URL", default="http://localhost:5173")
BACKEND_URL = os.environ.get(key="BACKEND_URL", default="http://localhost:8000/api/v1")
MAX_TRANSACTION_TIMEOUT = 100

CLIENT_DETAILS = {
    "username": "Cliente1" ,
    "email": "cliente1@gmail.com",
    "password": "Password123!"
}

MERCHANT_DETAILS = {
    "name": "Negoziante1",
    "partitaIVA": "12312312312",
    "address": "Via dei Tigli",
    "email": "negoziante1@gmail.com",
    "password": "Password123!"
}

PRODUCT_DETAILS = {
    "name": "Prodotto1",
    "description": "Descrizione del prodotto 1",
    "origin": "Italia",
    "points": 10
}

class DataProxy():
    merchant_id = None
    merchant_jwt = None
    
    client_jwt = None
    
    default_product_id = None
    
    @staticmethod
    def get_merchant_id_and_jwt():
        if DataProxy.merchant_id is None or DataProxy.merchant_jwt is None:
            finalUrl = f"{BACKEND_URL}/login"
            response = req.post(finalUrl, json={"email": MERCHANT_DETAILS["email"], "password": MERCHANT_DETAILS["password"]})
            if response.status_code == 200:
                DataProxy.merchant_id = response.headers.get("location").split("/")[-1]
                DataProxy.merchant_jwt = response.json().get("token")
            else:
                raise Exception(f"Failed to retrieve merchant ID. Status code: {response.status_code}, Response: {response.text}")
            
        return (DataProxy.merchant_id, DataProxy.merchant_jwt)
    
    @staticmethod
    def get_client_jwt():
        if DataProxy.client_jwt is None:
            finalUrl = f"{BACKEND_URL}/login"
            response = req.post(finalUrl, json={"email": CLIENT_DETAILS["email"], "password": CLIENT_DETAILS["password"]})
            if response.status_code == 200:
                DataProxy.client_jwt = response.json().get("token")
            else:
                raise Exception(f"Failed to retrieve client JWT. Status code: {response.status_code}, Response: {response.text}")
            
        return DataProxy.client_jwt
    
    @staticmethod
    def get_default_product_id():
        if DataProxy.default_product_id is None:
            merchant_id, _ = DataProxy.get_merchant_id_and_jwt()
            finalUrl = f"{BACKEND_URL}/shops/{merchant_id}/products"
            response = req.get(finalUrl)
            if response.status_code == 200:
                products = response.json()
                if products:
                    return products[0]["id"]
                else:
                    raise Exception("No products found for the merchant.")
            else:
                raise Exception(f"Failed to retrieve products. Status code: {response.status_code}, Response: {response.text}")

def register_default_client():
    finalUrl = f"{BACKEND_URL}/register/client"

    return req.post(finalUrl, json=CLIENT_DETAILS)

def register_default_merchant():
    finalUrl = f"{BACKEND_URL}/register/merchant"
    
    png_file = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x01\x00\x00\x0c\x00\x01\x04p\xcd\xa4\x00\x00\x00\x00IEND\xaeB`\x82'
    
    files = {
        'image': ('merchant_logo.png', io.BytesIO(png_file), 'image/png')
    }
    
    return req.post(finalUrl, data=MERCHANT_DETAILS, files=files)

def add_default_product(merchant_id, jwt):
    # Se il prodotto esiste già non fare nulla
    try:
        DataProxy.get_default_product_id()
        return "Product already exists"
    except Exception:   
        pass
    
    finalUrl = f"{BACKEND_URL}/shops/{merchant_id}/products"
    
    png_file = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x01\x00\x00\x0c\x00\x01\x04p\xcd\xa4\x00\x00\x00\x00IEND\xaeB`\x82'
    
    files = {
        'image': ('product_image.png', io.BytesIO(png_file), 'image/png')
    }
    
    return req.post(finalUrl, data=PRODUCT_DETAILS, files=files, headers={"Authorization": f"Bearer {jwt}"})

app = FastAPI()
app.mount("/html", StaticFiles(directory="html", html=True), name="html")

# Enum per i target
class ReqTarget(Enum):
    BACKEND = BACKEND_URL
    FRONTEND = FRONTEND_URL

# Enum per i verbi HTTP
class ReqType(Enum):
    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4

# Enum per gli endpoint
class ReqEndpoint(Enum):
    REGISTRATION_CLIENT = "/register/client"
    LOGIN = "/login"
    TRANSACTION_BEGIN = "/QRCodes/assignPoints"
    TRANSACTION_END = "/QRCodes/scanned"

# Funzione che data un'operazione ricevuta dall form HTML ritorna una tupla, il verbo HTTP e l'endpoint relativo
def strOperationToEnums(operation: str) -> (ReqType, ReqEndpoint):
    match operation:
        case "RegisterClient":
            return (ReqType.POST, ReqEndpoint.REGISTRATION_CLIENT)
        case "Login":
            return (ReqType.POST, ReqEndpoint.LOGIN)
        case "BeginTransaction":
            return (ReqType.POST, ReqEndpoint.TRANSACTION_BEGIN)
        case "EndTransaction":
            return (ReqType.POST, ReqEndpoint.TRANSACTION_END)

    raise ModuleNotFoundError

def decode_transaction_qrcode(qrcode: str) -> str:
    _, b64 = qrcode.split(",", 1)
    img = Image.open(io.BytesIO(base64.b64decode(b64)))

    return decode(img)[0].data.decode()

async def completeTransaction(transaction_token: str, jwt: str):
    delay = random.randint(1, MAX_TRANSACTION_TIMEOUT)
    await asyncio.sleep(delay)
    
    headers = {}
    if jwt:
        headers["Authorization"] = f"Bearer {jwt}"
        
    finalUrl = f"{BACKEND_URL}{ReqEndpoint.TRANSACTION_END.value}"
    
    try:
        req.post(finalUrl, headers=headers, json={"token": transaction_token})
    except Exception as e:
        print(f"Error while closing pending transaction: {e}")


# Funzione generica per fare richieste con parametri comuni come jwt e payload per POST ecc...
async def makeRequest(
    type: ReqType,
    target: ReqTarget, 
    endpoint: ReqEndpoint, 
    index: int = 0,
    payload: dict = None,
    errorRate: int = 0
) -> req.Response:
    headers = {}

    # --> Siccome ora abbiamo utenti di default, possiamo ricavarci noi i jwt
    # if jwt != "":
    #     headers["Authorization"] = f"Bearer {jwt}"

    finalUrl = f"{target.value}{endpoint.value}"
    
    # Controllo se l'url fa parte dei predefiniti, in tale caso applicare gli errrori
    error_trigger = random.randint(1, 100) <= errorRate
    match endpoint:
        case ReqEndpoint.REGISTRATION_CLIENT:
            if error_trigger:
                error_type = random.choice(["invalid_payload", "email_already_in_use"])
                match error_type:
                    case "invalid_payload":
                        # L'errore con payload invalido è implementato lasciando vuoto lo username, questo genererà un errore 400
                        payload = {
                            "username": "",
                            "email": f"email{time.time_ns()}_{index}@gmail.com",
                            "password": "Password123!"
                        }
                    case "email_already_in_use":
                        # L'errore con email già in uso è implementato inserendo "mariorossi@gmail.com" come email, questo genererà un errore 409
                        payload = {
                            "username": f"username{time.time_ns()}_{index}",
                            "email": CLIENT_DETAILS["email"],  # Email già in uso
                            "password": CLIENT_DETAILS["password"]
                        }
            else:
                payload = {
                    "username": f"username{time.time_ns()}_{index}",
                    "email": f"email{time.time_ns()}_{index}@gmail.com",
                    "password": "Password123!"
                }

        case ReqEndpoint.LOGIN:
            if error_trigger:
                # L'errore con credeniali errate è implementato lasciando vuota la password, questo genererà un errore 401
                payload = {
                    "email": "inesistente@gmail.com",
                    "password": ""
                }
            else:
                payload = {
                    "email": CLIENT_DETAILS["email"],
                    "password": CLIENT_DETAILS["password"]
                }


        case ReqEndpoint.TRANSACTION_BEGIN:
            headers = {"Authorization": f"Bearer {DataProxy.get_merchant_id_and_jwt()[1]}"}
            if error_trigger:
                # L'errore di prodotto invalido è implementato inserendo un productID inesistente, questo genererà un errore 400
                payload = [
                    {
                        "productID": "1", # Qui va inserito l'id del prodotto che non e' presente nel DB
                        "quantity": 1
                    }
                ]
            else:
                payload = [
                    {
                        "productID": DataProxy.get_default_product_id(), # Qui va inserito l'id del prodotto che mettiamo nel DB
                        "quantity": 1
                    }
                ]

    # Chiamata in base al metodo
    if type == ReqType.GET:
        return req.get(finalUrl, headers=headers)
    elif type == ReqType.POST:

        if endpoint != ReqEndpoint.TRANSACTION_BEGIN:
            return req.post(finalUrl, headers=headers, json=payload)
        else:
            response_begin = req.post(finalUrl, headers=headers, json=payload)
            
            if response_begin.status_code == 200:
                transaction_image = response_begin.text
                transaction_token = decode_transaction_qrcode(transaction_image)
                asyncio.create_task(completeTransaction(transaction_token, DataProxy.get_client_jwt()))
            
            return response_begin

    else:
        raise NotImplementedError("Request type not yet implemented")


@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("html/index.html")


@app.post("/instant_requests")
async def instant(
    requests: int = Form(), 
    operation: str = Form(),
    errorRate: int = Form(),
):
    try:
        for index in range(0, requests):
            (method, endpoint) = strOperationToEnums(operation)
            _ = asyncio.ensure_future(
                makeRequest(method, ReqTarget.BACKEND, endpoint, index, errorRate=errorRate)
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
    operation: str = Form(),
    errorRate: int = Form(),
):
    try:
        async def send_requests():
            for _ in range(0, duration):
                for index in range(0, requests):
                    (method, endpoint) = strOperationToEnums(operation)
                    __ = asyncio.ensure_future(
                        makeRequest(method, ReqTarget.BACKEND, endpoint, index, errorRate=errorRate)
                    )

                    # response = await __
                    # print(response.status_code)

                await asyncio.sleep(1)

        # Esegui l'invio delle richieste in modo asincrono per dare la risposta al browser
        asyncio.get_event_loop().create_task(send_requests())
    except Exception as e:
        print(e)
        return f"Error: {e}"
    return "Requests queued"

@app.post("/distributed_requests")
async def distributed(
    requests: int = Form(),
    duration: int = Form(),
    operation: str = Form(),
    errorRate: int = Form(),
):
    try:
        async def send_requests():
            interval = duration / requests

            for index in range(0, requests):
                (method, endpoint) = strOperationToEnums(operation)
                
                __ = asyncio.ensure_future(
                    makeRequest(method, ReqTarget.BACKEND, endpoint, index, errorRate=errorRate)
                )
                
                await asyncio.sleep(interval)

        # Esegui l'invio delle richieste in modo asincrono per dare la risposta al browser
        asyncio.get_event_loop().create_task(send_requests())
    except Exception as e:
        print(e)
        return f"Error: {e}"
    return "Requests queued"

@app.post("/prepare_data")
async def prepare_data():
    register_default_client()
    register_default_merchant()
    
    # Recupera l'ID del merchant e il JWT per aggiungere il prodotto predefinito
    merchant_id, jwt = DataProxy.get_merchant_id_and_jwt()
    add_default_product(merchant_id, jwt)

if __name__ == "__main__":
    PORT = int(os.environ.get(key="SIM_PORT", default=8050))
    reload = False
    if bool(os.environ.get("DEBUG", False)):
        reload = True
    uvicorn.run("main:app", port=PORT, reload=reload)