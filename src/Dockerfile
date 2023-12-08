# Use an official Python runtime as a parent image
FROM python:3.11.0

WORKDIR /app
ADD ./src /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]