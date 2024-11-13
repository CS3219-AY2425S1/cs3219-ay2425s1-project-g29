# Matching Service

This service provides an matching service for users to interact with.

## Features

- **Real-time user matching based on categories and difficulty.**
- **Each user will wait for 30 seconds to find a match.**
- **Support for both complete (topic and difficulty) and partial (topic) matches.**
- **Cancel the matching request any time during the 30 seconds waiting period**
- **Pressing the refresh button will cancel the on going match request**
- **Dockerized setup for easy deployment and testing.**

## Run the Matching Service

Ensure Docker Desktop is running before proceeding.

To start the Matching Service, run the following command from the root directory where the `docker-compose.yml` file is located:

```bash
docker compose up
```
