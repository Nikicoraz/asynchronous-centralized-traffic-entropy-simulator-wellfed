FROM alpine

RUN apk add --no-cache python3 py3-pip zbar

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt --break-system-packages

COPY . .

EXPOSE 8050
CMD [ "python3", "main.py" ]
