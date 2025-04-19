<H1 style="text-align: center;"> SimCode - A collaborative code editing and execution platform </H1>
<H3 style="text-align: center;"> Submission by Team 15: Mavericks for CS6.401 Software Engineering Project 3</H3>

## Team Details
- Aashrey Jain -- 2024202012
- Aarathi Baburaj -- 2024201083
- Akhila Anumalla -- 2024201084
- Kritika Joshi -- 2024201013
- S Supraja -- 2024202014

## Description

**SimCode** is a real-time collaborative code editing and execution platform built using **React, FastAPI, and WebSockets**. It allows multiple users to join a virtual room and write code together seamlessly across different programming languages.  

Users can specify pre-execution shell commands and run their code in an isolated Docker container with instant feedback. The platform displays both `stdout` and `stderr` outputs, supporting transparent code testing and review. Designed for education, interviews, and teamwork, SimCode emphasizes simplicity, speed, and collaboration.

### Features

- Real-time and conflict-free code sync across connected editors
- Sandboxed code execution directly in the browser
- Support for languages like C++, Python, Java, Javascript, and Bash
- Ability to enter bash prerequisites to setup execution environment
- Supports upto 8 concurrent users at a time
- Light-weight and easy to use web application with customizable theme

## Prerequisites and Assumptions

The platform uses Websockets and has been tested on a Linux machine. The following tools are assumed to be pre-installed on the system; please ensure these are met before trying to run:

- Python 3.12 or higher
- Node v18.19.1
- Docker v28.1.1
- PostgreSQL


The following steps guide through the setup of the execution environment:

1. Create a virtual environment for the backend and install dependencies
    ```
    cd backend/
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt
    ```

2. Install frontend dependencies
    ```
    cd frontend/
    npm install
    ```

3. Ensure that the user trying to run the backend has superuser (`sudo`) privileges and passwordless sudo setup for Docker. The user should also be added to the `docker` group so that code execution works.

    a. Edit the sudoers file using `sudo visudo` and add the following line:
    
        <your_username> ALL=(ALL) NOPASSWD: /usr/bin/docker

 
    b. Add the user to the `docker` group:

        sudo usermod -aG docker <your_username>

4. Ensure that PostgreSQL is running and the intended database has been created.

5. Setup `.env` file for the backend. In this file, add the database-related parameters. Sample `.env` for the backend:
    ```
    DB_USER="postgres"
    DB_PASS=""
    DB_NAME="testdb"
    DB_SOCKET="localhost:5432"
    ```

6. Setup `.env` file for the frontend. In this file, add the URL and port where the server is running. This is the configuration used by both React and Websocket. Ensure that the port is same for both. Sample `.env` file for the frontend:
    ```
    REACT_APP_BACKEND_URL="http://localhost:8000"
    SERVER_PORT=8000
    ```

## How to Run

Follow the following steps to start the platform:

1. Start the backend:
    ```
    cd backend/
    source .venv/bin/activate
    uvicorn main:simcode --port <desired port>
    ```

2. Start the frontend:
    ```
    cd frontend/
    npm start
    ```

3. Navigate to `http://localhost:3000/` in your browser, if you're not automatically redirected.

4. **Get Coding!**
---