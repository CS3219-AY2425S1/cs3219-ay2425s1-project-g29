[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/bzPrOe11)
# CS3219 Project (PeerPrep) - AY2425S1

![Peerprep Logo](docs/PeerPrep.png)
## Group: G29

## What is Peerprep?
A technical interview preparation platform and peer matching system, where students can find peers to practice interview questions together.

## Frontend Stack
### Using Nuxt.js for Frontend framework using vue
- Auto-import
- easy folder structure
- lightweight
- easy to deploy
- Decent module support

## Backend Stack
### Flask (Python)
- Lightweight
- easy to deploy
- fast
- easy to test

### Kafka
- For asynchronous events
- Matching and Queueing
- reliable
- scalable

### Third-Party Services
- Firebase (database and authentication)
- Liveblocks (real-time code editor)
- Openai (gpt API)

## Setup (Local)
### Environment Vairables
Set up environment variables in the root of the following directories
- [Frontend/Peerprep](frontend/Peerprep/)
  - `.env` must have 4 variables
  - FIREBASE_API_KEY 
  - LB_API_KEY 
  - HOST_ADDRESS="localhost" (default)
  - OPENAI_API_KEY

- [chat_service](backend/chat_service/)
  - `.env` must have `CRED_PATH` which is `"./firebase-cred.json"` by default
  - `firebase-cred.json` which contains the firebase credentials from firebase service accounts

- [question_service](backend/question_service/)
  - `.env` must have `CRED_PATH` which is `"./firebase-cred.json"` by default
  - `firebase-cred.json` which contains the firebase credentials from firebase service accounts

- [user_service](backend/user_service/)
  - `.env` must have `CRED_PATH` which is `"./firebase-cred.json"` by default
  - `firebase-cred.json` which contains the firebase credentials from firebase service accounts

### Using Docker Compose
- Make sure you have the following installed
  - [Docker](https://docs.docker.com/engine/install/)
  - [Docker Compose](https://docs.docker.com/compose/install/)
- Run the following in the root directory of this project
```bash
docker compose up --build
```

NOTE: For both Docker Compose and Manual starting you will want to **wait for 30 seconds** for the services to mount properly before using the application. Even if all services are up the delay is necessary. 

### Manually
- Make sure you have the following installed
  - [Python 3.8](https://www.python.org/downloads/)
  - [NodeJS LTS](https://nodejs.org/en/)
- Setup the backend services first following the `README.md` in each folder.
- Run the microservices.
- Follow the steps in the `README.md` in `frontend/Peerprep` to setup the frontend.
- Run the frontend using `npm run dev` in the [frontend/Peerprep](frontend/Peerprep/) directory
