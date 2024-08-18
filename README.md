## Create virtual environment

python -m venv venv

## Install the dependencies

pip install -r requirements.txt

## Use hosted Milvus DB and update the below env variables 

MILVUS_URI= <br/>
MILVUS_API_KEY=<br/>

## Use hosted Mongo DB and update the below env var

DATABASE_URL=

## Visualise milvus

You can use ziliz cloud vector DB vidualizer to view the contents

<img width="1485" alt="image" src="https://github.com/user-attachments/assets/ed73f89e-d52d-426f-88d2-fcfdde74e6b1">


## Setting up tika ( document parser )

docker pull apache/tika <br/>
docker run -d -p 127.0.0.1:9998:9998 apache/tika <br/>

Set environment variable for Tika <br/>
TIKA_SERVER_URL = 'http://localhost:9998/tika'<br/><br/>

Note: Prefer to use a hosted one

## Setting up prisma

From root directory run the below commands

`prisma generate` <br/>
`prisma db push`

## Running the app

uvicorn main:app --reload --port 8080

