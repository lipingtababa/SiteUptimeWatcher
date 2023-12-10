FROM python:3.11.0

WORKDIR /app

# Add the current directory contents into the container at /app
ADD ./ /app

RUN apt update && apt install -y net-tools 
RUN apt install -y tcpdump

RUN pip install --no-cache-dir -r test/requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

CMD ["uvicorn", "test.server.TestServer:app", "--host", "0.0.0.0", "--reload", "--timeout-keep-alive", "305", "--log-level", "error"]