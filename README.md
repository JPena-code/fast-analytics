<div align="center">
    <h1 style="font-size: 64px">FastAnalytics</h1>
    <p style="font-style: italic">
        <strong>Fast</strong>, easy and ready to go API to handle and capture analytics for your end API
    </p>
    <img src="https://img.shields.io/github/actions/workflow/status/JPena-code/analytics-retrieval-template/ci.yml?branch=main" alt="Build Status">
    <img src="https://img.shields.io/github/license/JPena-code/analytics-retrieval-template" alt="License">
    <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python Version">
    <img src="https://img.shields.io/badge/docker-supported-blue" alt="Docker">
    <img src="https://img.shields.io/codecov/c/github/JPena-code/analytics-retrieval-template" alt="Coverage">
    <img src="https://img.shields.io/badge/contributions-welcome-brightgreen" alt="Contributions">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit" alt="Pre-commit">
</div>

---

## Table of Contents

<details>
<summary>Click to expand</summary>

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Development](#development)
- [API Endpoints](#api-endpoints)
  - [Base URL](#base-url)
  - [Example Endpoints](#example-endpoints)
    - [Retrieve Events](#retrieve-events)
    - [Add Event](#add-event)
    - [Aggregated Events](#aggregated-events)
- [Examples](#examples)
  - [Python Client Example](#python-client-example)
- [Future Tasks](#future-tasks)
- [License](#license)

</details>

---

## Overview

The `FasAnalytics` project is a robust Analytics API designed for efficient information retrieval. Built with FastAPI, it leverages TimescaleDB for managing time-series data. The modular architecture ensures scalability and maintainability.

This project was inspired by the concepts and techniques demonstrated in [this video](https://www.youtube.com/watch?v=tiBeLLv5GJo&t=9420s) by **jmitchel3**. The video provided valuable insights into building scalable and efficient APIs, which greatly influenced the design and implementation of this project. Full credit goes to the author for their excellent content and inspiration.

---

## Features

- **FastAPI Backend**: High-performance Python web framework.
- **TimescaleDB Integration**: Optimized for time-series data.
- **Modular Design**: Easy to extend and maintain.
- **Pre-commit Hooks**: Ensures code quality and consistency.
- **Docker** Docker build and deploy integration

---

## Getting Started

### Prerequisites

- Docker
- Python 3.10+
- TimescaleDB

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/JPena-code/fast-retrieval.git
   cd fastanalytics
   ```

2. Build the Docker container:

   ```bash
   docker build -t fastanalytics .
   ```

3. Run the image created, the environment variables can be pass over the command line with the `-e or --env-file` argument (take as reference [.app.env.example](.app.env.example) to see expected environment variables), or mounting a volume in the containing with an .env file and pass the path to that file as an argument to the `docker run` command:

   ```bash
   # using a .env file mounted in container
   docker run -v <local-path>:<container-path> fastanalytics <container path>

   # using -e or --env-file
   docker run -e ENVIRONMENT=prod -e TIMEZONE=UTC -e ... fastanalytics
   docker run --env-file ./.env fastanalytics
   ```

---

### Development

To run the project locally for development purposes, follow these steps:

1. **Set up a Python virtual environment** (recommended):

  ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 -m fastanalytics
  ```

## API Endpoints

### Base URL

```text
http://localhost:8000/api/{version}
```

### Example Endpoints

#### Retrieve Events

- **GET** `/events`
  - Description: Fetch a list of events.
  - Response:

    ```json
    {
      "metadata": {
        "status": "success",
        "message": "string",
        "pagination": {
          "pageSize": 500,
          "page": 1,
          "totalRecords": 0,
          "totalPages": 0
        },
        "timestamp": "string"
      },
      "errors": [
        {
          "additionalProp1": "string",
          "additionalProp2": "string",
          "additionalProp3": "string"
        }
      ],
      "results": [
        {
          "page": "/hone",
          "agent": "stringstri",
          "ipAddress": "string",
          "referrer": "https://example.com/",
          "sessionId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
          "duration": 0,
          "id": 0,
          "time": "2025-11-25T04:41:57.539Z"
        }
      ]
    }
    ```

#### Add Event

- **POST** `/events`
  - Description: Add a new event.
  - Request Body:

    ```json
    {
      "page": "/hone",
      "agent": "stringstri",
      "ip_address": "string",
      "referrer": "https://example.com/",
      "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "duration": 0
    }
    ```

  - Response:

    ```json
    {
      "metadata": {
        "status": "success",
        "message": "string",
      },
      "errors": [
        {
          "additionalProp1": "string",
          "additionalProp2": "string",
          "additionalProp3": "string"
        }
      ],
      "result": {
        "page": "/hone",
        "agent": "stringstri",
        "ipAddress": "string",
        "referrer": "https://example.com/",
        "sessionId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "duration": 0,
        "id": 0,
        "time": "2025-11-25T04:45:39.162Z"
      }
    }
    ```

#### Aggregated Events

- **GET** `/aggregate/{filed}`
  - Description: Return the aggregation of the duration by {field}
  - Response:

  ```json
  {
    "metadata": {
      "status": "success",
      "message": "string",
      "pagination": {
        "pageSize": 500,
        "page": 1,
        "totalRecords": 0,
        "totalPages": 0
      },
      "timestamp": "string"
    },
    "errors": [
      {
        "additionalProp1": "string",
        "additionalProp2": "string",
        "additionalProp3": "string"
      }
    ],
    "results": [
      {
        "field": "string",
        "interval": "2025-11-25T04:47:44.602Z",
        "count": 0,
        "avgDuration": 0,
        "minDuration": 0,
        "maxDuration": 0
      }
    ]
  }
  ```

---

## Examples

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api/{version}"

# Fetch events
response = requests.get(f"{BASE_URL}/events")
print(response.json())

# Add an event
data = {
    "path": "/new/path",
    "agent": "new-agent",
    "ip_address": "192.168.0.1",
    "session_id": "new-session"
}
response = requests.post(f"{BASE_URL}/events", json=data)
print(response.json())
```

---

## Future Tasks

- **Authentication**: Implement OAuth2 for secure access.
- **TimingMiddleware**: Implement custom middleware for timing
- **CorrelationalMiddleware**: Implement custom correlational Middleware
- **Custom Error**: Define a custom schema of errors to notify when something goes wrong
- **CI/CD Integration**: Automate testing and deployment.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
