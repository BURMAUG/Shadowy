FROM python:3.9-slim

LABEL authors="dj"

WORKDIR /app

#COPY . /app

COPY ./requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

ENV DISPLAY=:99

# Copy path to my local db to the containerize app
COPY /Users/dj/Desktop/job_db.repository /app/db/job_db.repository

COPY . /app

CMD ["python", "main.py"]

#ENTRYPOINT ["top", "-b"]