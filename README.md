## Use hosted Milvus DB and update the below env variables 

MILVUS_URI= <br/>
MILVUS_API_KEY=


## Visualise milvus

You can use ziliz cloud vector DB vidualizer to view the contents

## Setting up tika ( document parser )

docker pull apache/tika <br/>
docker run -d -p 127.0.0.1:9998:9998 apache/tika <br/>
Set environment variable for Tika <br/>
TIKA_SERVER_URL = 'http://localhost:9998/tika'<br/><br/>

Note: Prefer to use a hosted one

## Setting up prisma

From root directory run the below commands

`prisma generate`
`prisma db push`

## Running the app

uvicorn main:app --reload --port 8080

