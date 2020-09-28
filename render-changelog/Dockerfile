FROM python:3.8-alpine

WORKDIR /code

RUN apk add --no-cache git

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY script.py .

ENTRYPOINT ["python", "/code/script.py"]

