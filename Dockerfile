FROM python:3.11.0

# I do need netstats and tcpdump for debugging
RUN apt update && apt install -y net-tools 
RUN apt install -y tcpdump

WORKDIR /app

# Add the current directory contents into the container at /app
ADD ./ /app

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 8000 is used by the test server
EXPOSE 8000
# 8080 is used by the API
EXPOSE 8080

CMD ["./entrypoint.sh"]
