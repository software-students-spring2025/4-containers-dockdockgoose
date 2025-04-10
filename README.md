
![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

[![ML Client CI](https://github.com/software-students-spring2025/4-containers-dockdockgoose/actions/workflows/mlclient.yml/badge.svg)](https://github.com/software-students-spring2025/4-containers-dockdockgoose/actions/workflows/mlclient.yml)

[![Web App CI](https://github.com/software-students-spring2025/4-containers-dockdockgoose/actions/workflows/webapp.yml/badge.svg)](https://github.com/software-students-spring2025/4-containers-dockdockgoose/actions/workflows/webapp.yml)

# Containerized App Exercise

Build a containerized app that uses machine learning. See [instructions](./instructions.md) for details.

## Team Members of DOCKDOCKGOOSE

- [Harini Buddaluru] (https://github.com/peanutoil)
- [Clarissa Choi] (https://github.com/clammy424)
- [Franyel Diaz Rodriguez] (https://github.com/Franyel1)
- [Tony Liu] (https://github.com/tony102809)

## Concept

The concept of our web app is to act as a calorie counter. 

We aim to streamline the process of counting calories as well as make it more accurate by using AI. 
This will help many along their journey with fitness and dieting. 

Within our project, we created a system of interworked Docker containers.
Our project uses a machine learning client in our web app interface. 
We incorporated a data base to track and collect the input. 

We used Gemini as our machine learning client. We used data collected from the camera as an input. 
You can collect data through the camera by capturing an image of the food. 

Upon capturing the image, we feed the image and prompt into the machine learning client. 

If the machine learning client does not detect a food, it will return an error. 
If the machine learning client detects a food, it will return the calories associated with the food. 

## Setup Instructions

To get our container up and running, follow the steps below. 

---

### 1. Install Python (if needed)

### 2. Install Docker Desktop (if needed)

### 3. Navigate to root directory

cd path-to-project/4-containers-dockdockgoose

### 4. Run the Project

docker compose build
docker compose up

### 5. Access Application

Once the docker container is built, you can access the web app by entering the below into your browser:
http://localhost:5000


## Standup Meetings

### Standup Report - April 8th, 2025
---

Franyel 
- did: Set up Docker and MongoDB
- doing: Testing Gemini API 
- blockers: none

Clarissa
- did: Making taskboard 
- doing: Starting frontend
- blockers: none

Tony
- did: Nothing yet
- doing: Helping with front and backend 
- blockers: Test for another class 

Harini
- did: Research
- doing: Login page
- blockers: none

### Standup Report - April 9th, 2025
---

Franyel 
- did: tested Gemini API
- doing: tests for ml client and web app
- blockers: none

Clarissa 
- did: frontend
- doing: readme
- blockers: none

Tony 
- did: edited home page
- doing: run pytests
- block: none

Harini 
- did: login page
- doing: home page
- blockers: none
