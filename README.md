## Install Milvus in Docker

curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh

bash standalone_embed.sh start

## Stop and delete milvus

bash standalone_embed.sh stop

bash standalone_embed.sh delete

## Visualise milvus

docker run -p 8000:3000 -e MILVUS_URL={your local IP address}:19530 zilliz/attu:v2.4
IP address should not be - localhost/127.0.0.1/0.0.0.0
Find out the local ip address using - ipconfig getifaddr en0
To check attu running, go here - http://localhost:8000 and login using your local IP address

## Running the app

uvicorn main:app --reload --port 8080

