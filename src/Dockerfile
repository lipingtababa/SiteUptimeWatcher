FROM python:3.11.0

RUN apt update && apt install -y net-tools
RUN apt install -y tcpdump

WORKDIR /app
ADD . /app

RUN pip install --no-cache-dir -r src/requirements.txt

CMD ["sh", "-c", "exec python src/main.py"]
