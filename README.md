# Cloud Security Event Monitor

A cloud-ready security event monitoring system that simulates security events from multiple servers, processes them asynchronously, detects suspicious login activity, and displays security alerts through a web dashboard.

---

## Overview

**Cloud Security Event Monitor** is a distributed, containerized security monitoring application designed to demonstrate how cloud computing concepts can be applied to security event processing.

The system simulates three servers generating security events:

- Successful logins
- Failed logins
- File access

Events are submitted through a web dashboard and sent to a FastAPI backend. The backend places events into a Redis message queue, and a separate security worker processes them asynchronously.

The worker analyzes events and detects a possible brute-force login pattern.

### Detection Rule

If **three login failures are generated for the same server/IP**, the system creates:

`POSSIBLE_BRUTE_FORCE`

Each server is monitored independently, so activity from one server does not affect the failure count of another server.

---

## Problem Statement

In a distributed or cloud environment, multiple servers can continuously generate security-related events.

Processing every event directly through the main application can couple event collection with security analysis and make the architecture harder to scale.

This project demonstrates a simple architecture where:

```text
Event Collection
       ↓
Message Queue
       ↓
Background Processing
       ↓
Security Detection
       ↓
Data Storage
       ↓
Dashboard
```

This separation allows event ingestion and security analysis to operate as independent components.

---

## Main Idea

The core idea is to build a small distributed security monitoring system using cloud and distributed-system concepts.

Instead of processing everything inside one application component, the system separates event collection from event analysis.

### Architecture

```text
                    ┌───────────────┐
                    │    Browser    │
                    │   Dashboard   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    FastAPI    │
                    │   Backend/API │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │     Redis     │
                    │ Message Queue │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Security    │
                    │    Worker     │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    SQLite     │
                    │    Database   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Dashboard   │
                    │ Events/Alerts │
                    └───────────────┘
```

---

## System Architecture

### 1. Client / Web Dashboard

The frontend provides a simple interface for:

- Selecting one of the simulated servers
- Generating security events
- Viewing total events
- Viewing security alerts
- Viewing monitored servers
- Viewing recent events

The frontend communicates with the backend through HTTP requests.

**Technologies:** HTML, CSS, JavaScript

---

### 2. FastAPI Backend

The backend acts as the application's API layer.

It is responsible for:

- Receiving events from the frontend
- Validating event data
- Sending events to the processing queue
- Providing event data to the dashboard
- Providing alert data
- Providing system statistics
- Providing the list of monitored servers

**Technology:** Python + FastAPI

FastAPI provides the HTTP API used by the frontend.

---

### 3. Redis Message Queue

Redis is used as an intermediate message queue between the API and the security worker.

Instead of making the API perform security analysis itself:

```text
API
 ↓
Queue
 ↓
Worker
```

the API places an event into Redis.

The security worker then retrieves the event and processes it.

### Why Redis?

Redis provides a lightweight mechanism for asynchronous communication between application components.

It demonstrates an important distributed and cloud-computing concept:

> **Decoupling event producers from event consumers.**

The API and worker therefore do not need to perform all processing inside the same application component.

---

### 4. Security Worker

The security worker is a separate Python process responsible for event processing.

Its responsibilities include:

1. Reading events from Redis
2. Identifying the server associated with the event
3. Tracking login failures independently for each server/IP
4. Detecting suspicious login patterns
5. Creating security alerts
6. Storing the resulting information

The worker is intentionally separated from the API so that event collection and security analysis are independent responsibilities.

---

## Security Detection Logic

The prototype currently implements a simple brute-force detection rule.

Three simulated servers are monitored:

| Server | IP Address |
|---|---|
| Server-01 | `10.0.0.11` |
| Server-02 | `10.0.0.12` |
| Server-03 | `10.0.0.13` |

The supported event types are:

```text
LOGIN_SUCCESS
LOGIN_FAILURE
FILE_ACCESS
```

### Example

Suppose Server-01 generates:

```text
LOGIN_FAILURE
LOGIN_FAILURE
LOGIN_FAILURE
```

The worker detects the pattern and generates:

```text
POSSIBLE_BRUTE_FORCE
```

with a reason similar to:

```text
3 failed logins detected for 10.0.0.11
```

### Independent Server Tracking

The failure count is maintained separately for each server/IP.

For example:

```text
Server-01 → 2 failures
Server-02 → 1 failure
Server-03 → 0 failures
```

If another failure occurs on Server-01:

```text
Server-01 → 3 failures
```

an alert is generated.

Failures from Server-02 or Server-03 do not contribute to Server-01's count.

---

## Event Simulation

The project does not connect to real production servers.

Instead, the dashboard provides a controlled **Event Simulator**.

The user selects:

1. A simulated server
2. An event type

and submits one event at a time.

This makes it possible to demonstrate security-event processing without requiring access to real server infrastructure.

### Simulated Infrastructure

```text
Server-01 → 10.0.0.11
Server-02 → 10.0.0.12
Server-03 → 10.0.0.13
```

The simulation allows the system's distributed event-processing workflow to be demonstrated safely and reproducibly.

---

## Complete Event Workflow

```text
1. User selects a server
        ↓
2. User selects an event type
        ↓
3. Frontend sends event to FastAPI
        ↓
4. FastAPI validates and accepts the event
        ↓
5. Event is placed into Redis
        ↓
6. Security Worker consumes the event
        ↓
7. Worker analyzes the event
        ↓
8. Login-failure state is updated
        ↓
9. Suspicious pattern is detected
        ↓
10. Alert is generated when the threshold is reached
        ↓
11. Event/alert information is stored in SQLite
        ↓
12. Dashboard retrieves updated information
        ↓
13. User sees the event and security alert
```

---

# Cloud Computing Concepts Demonstrated

## 1. Client-Server Architecture

The browser acts as the client.

The FastAPI application acts as the server.

```text
Client
  ↓ HTTP
FastAPI Server
```

The client does not directly access the database or security worker.

---

## 2. Distributed Processing

The API and security worker are separate processes.

```text
API
 ↓
Redis
 ↓
Worker
```

This demonstrates how different components can perform different responsibilities within a distributed application.

---

## 3. Asynchronous Processing

The API does not need to perform the entire security-analysis operation while handling the incoming request.

Instead:

```text
Event
 ↓
Redis Queue
 ↓
Worker processes event
```

This separates event ingestion from event analysis.

---

## 4. Message Queue

Redis acts as the communication layer between the API and the worker.

```text
Producer              Consumer
   │                     │
   ▼                     ▼
FastAPI → Redis → Security Worker
```

The API is the producer and the security worker is the consumer.

---

## 5. Containerization

The application is containerized using Docker.

The project contains separate services for:

```text
FastAPI
Redis
Security Worker
```

Docker Compose is used to run these components together.

This makes the application environment reproducible and simplifies deployment.

---

## 6. Service Separation

The system separates responsibilities into different services:

| Component | Responsibility |
|---|---|
| Frontend | User interaction and visualization |
| FastAPI | API and event ingestion |
| Redis | Message queuing |
| Worker | Security processing |
| SQLite | Persistent application data |

This separation makes the architecture easier to understand, test, and deploy.

---

## 7. Cloud Deployment

The application is designed to be deployed on a cloud virtual machine using:

**AWS EC2**

The intended deployment architecture is:

```text
                   Internet
                      │
                      ▼
              ┌───────────────┐
              │    AWS EC2    │
              │ Ubuntu Server │
              └───────┬───────┘
                      │
                Docker Compose
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
    FastAPI          Redis         Worker
       │                             │
       └──────────────┬──────────────┘
                      ▼
                   SQLite
                      │
                      ▼
                  Dashboard
```

AWS EC2 provides the cloud virtual machine on which the containerized application can run.

---

# Container Architecture

Docker Compose manages the application services.

```text
Docker Compose
│
├── API Container
│     └── FastAPI
│
├── Redis Container
│     └── Message Queue
│
└── Worker Container
      └── Security Processing
```

This allows all required services to be started together.

---

# Database

The project uses:

**SQLite**

SQLite stores application data such as:

- Security events
- Generated alerts
- Event-related information used by the dashboard

SQLite is suitable for this prototype because the goal is to demonstrate the architecture and event-processing workflow without introducing the operational complexity of a separate production database server.

---

# Automated Testing

The project includes automated tests using:

**pytest**

The test suite contains:

- API-level tests
- Security detection tests

The current automated test suite contains **6 tests**, covering the API and security-detection behavior.

The Docker-based test run verifies:

```text
6 tests collected
6 tests passed
```

---

# Continuous Integration

GitHub Actions is used for automated CI.

The workflow is triggered when code is pushed to GitHub or when a pull request is created.

The CI pipeline performs:

```text
Git Push / Pull Request
        ↓
GitHub Actions
        ↓
Build Docker Images
        ↓
Start Redis
        ↓
Run pytest
        ↓
Tests Pass → Workflow succeeds
Tests Fail → Workflow fails
```

This ensures that automated tests are executed in the Docker-based project environment rather than relying only on manual testing.

A failed test causes the GitHub Actions workflow to fail.

---

# Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | HTML, CSS, JavaScript | Dashboard and event simulation |
| Backend | Python | Application logic |
| API | FastAPI | HTTP API and event ingestion |
| Queue | Redis | Asynchronous event communication |
| Worker | Python | Security event processing |
| Database | SQLite | Event and alert storage |
| Containerization | Docker | Application isolation |
| Orchestration | Docker Compose | Running multiple services |
| Testing | pytest | Automated tests |
| Version Control | Git | Source-code management |
| Repository | GitHub | Source-code hosting |
| CI | GitHub Actions | Automated testing |
| Cloud Platform | AWS | Cloud infrastructure |
| Cloud Compute | AWS EC2 | Hosting the application |

---

# Project Structure

```text
cloud-security-event-monitor/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── queue.py
│   ├── security.py
│   │
│   └── static/
│       └── index.html
│
├── tests/
│   ├── test_api.py
│   └── test_security.py
│
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
├── worker.py
├── README.md
└── .gitignore
```

---

# Running the Project Locally

## Prerequisites

Install:

- Docker
- Docker Compose
- Git

## Clone the Repository

```bash
git clone https://github.com/humita-bhatia/cloud-security-event-monitor.git
cd cloud-security-event-monitor
```

## Start the Application

```bash
docker compose up --build
```

Docker Compose starts:

```text
API
Redis
Security Worker
```

The application runs on:

```text
http://localhost:8000
```

Open the address in a browser.

---

# Run Tests

The automated tests can be run through Docker using:

```bash
docker compose run --rm api pytest
```

The test suite should report all tests as passing.

---

# Example Demonstration

A simple demonstration of the detection mechanism:

### Step 1

Select:

```text
Server-01
LOGIN_FAILURE
```

Send the event.

### Step 2

Send another:

```text
Server-01
LOGIN_FAILURE
```

### Step 3

Send a third:

```text
Server-01
LOGIN_FAILURE
```

### Result

The worker detects the threshold:

```text
POSSIBLE_BRUTE_FORCE
```

The dashboard then displays the security alert.

---

# What Is Simulated?

This project is a **prototype security monitoring system**.

The following are simulated:

- Security events
- Server identities
- Server IP addresses
- Login activity
- File-access activity
- Brute-force-like behavior

The system does **not** connect to real production servers or perform real intrusion detection.

The purpose is to demonstrate:

- Cloud architecture
- Distributed processing
- Message queues
- Background workers
- Containerization
- Automated testing
- Continuous integration
- Cloud deployment concepts

---

# Cloud Computing Learning Objectives

This project demonstrates practical implementation of:

- Client-server architecture
- Distributed systems
- Asynchronous processing
- Message queues
- Service decoupling
- Containerization
- Multi-container application architecture
- Cloud deployment
- Continuous integration
- Automated testing

The project connects these concepts into a single working application rather than demonstrating them independently.

---

# Future Improvements

Possible extensions include:

- Support for additional security-event types
- More sophisticated detection rules
- Authentication and authorization
- Persistent cloud database
- Multiple worker instances
- Real-time event streaming
- HTTPS
- Production-grade logging
- More advanced anomaly detection
- Automatic cloud deployment through CI/CD

These features are **not part of the current prototype**.

---

# Author

**Humita Bhatia**

B.Tech — Computer Science Engineering

---

## License

This project is developed as an academic Cloud Computing project.
