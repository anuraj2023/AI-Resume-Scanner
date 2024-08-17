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

## Setting up tika ( document parser )

docker pull apache/tika
docker run -d -p 127.0.0.1:9998:9998 apache/tika
Set environment variable for Tika 
TIKA_SERVER_URL = 'http://localhost:9998/tika'

## Setting up prisma

From root directory run the below commands

`prisma generate`
`prisma db push`

## Running the app

uvicorn main:app --reload --port 8080

