# Cloud Security Event Monitor

A small cloud-ready distributed security event monitoring system.

## What it does

The dashboard provides three simulated servers. A user can select a server and send one of three events: `LOGIN_SUCCESS`, `LOGIN_FAILURE`, or `FILE_ACCESS`.

Each event is placed into a Redis message queue. A separate security worker consumes the events, stores them in SQLite, and checks for a simple suspicious pattern: three consecutive failed logins from the same server and IP. When the third failure is processed, the worker creates one `POSSIBLE_BRUTE_FORCE` alert. The failure counter for that server/IP is then reset, so a later group of three failures can create a new alert.

## Architecture

Client/Dashboard → FastAPI → Redis Queue → Security Worker → SQLite → Dashboard

The API and worker are separate services and communicate asynchronously through Redis. Docker Compose runs the API, worker, and Redis as separate containers.

## Technologies

- Python + FastAPI
- Redis message queue
- SQLite
- Docker / Docker Compose
- Pytest
- GitHub Actions

## Run locally

```bash
docker compose up --build
```

Open `http://localhost:8000`.

Choose a server and send events from the Event Simulator. To demonstrate detection, click **Login Failure** three times for the same server.

## Tests

The project includes tests for event handling and the brute-force detection rule. GitHub Actions runs the test suite on pushes and pull requests.
