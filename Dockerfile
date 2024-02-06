FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install ffmpeg libsm6 libxext6  -y &&\
    apt-get install -y tesseract-ocr-all

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY src /app/src

ENV UVICORN_SERVER_HOST "0.0.0.0"
ENV UVICORN_SERVER_PORT "8888"

CMD python -m src.app
