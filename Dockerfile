FROM python:3.12.3

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


RUN apt update 
RUN apt upgrade -y 
RUN apt install -y nano unixodbc unixodbc-dev libgl1 libglib2.0-0

WORKDIR /app

COPY requirements.txt requirements-ai.txt ./

RUN pip install -r requirements.txt -r requirements-ai.txt

COPY . .

RUN chmod 777 entrypoint.sh

