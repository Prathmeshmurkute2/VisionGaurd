# 🎥 Intelligent Video Surveillance System

An AI-powered, full-stack video surveillance platform that analyzes live or recorded video streams to detect, track, and monitor objects in real time.

The system combines **computer vision, object detection, object tracking, analytics, authentication, persistent storage, REST APIs, and real-time WebSocket communication** into a single surveillance application.

---

## 🚀 Overview

Traditional CCTV systems primarily record video and require humans to continuously monitor the footage.

This project aims to make surveillance more intelligent by automatically analyzing video streams and extracting useful information such as detected objects, tracking data, events, and analytics.

### High-Level Architecture

```text
                 ┌─────────────────────┐
                 │   Video Source      │
                 │ Camera / Video File │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │   Video Processing  │
                 │      Pipeline       │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Object Detection    │
                 │      + Tracking     │
                 └──────────┬──────────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
        ┌─────────┐    ┌─────────┐    ┌─────────┐
        │ Events  │    │Analytics│    │Database │
        └─────────┘    └─────────┘    └─────────┘
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                 ┌─────────────────────┐
                 │     FastAPI API     │
                 │    + WebSockets     │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │    React Frontend   │
                 │   Dashboard / UI    │
                 └─────────────────────┘
```

---

## ✨ Features

### 🤖 AI-Powered Detection

* Real-time object detection from video streams
* Computer-vision based analysis
* Configurable confidence threshold
* Support for processing live or recorded video

### 🎯 Object Tracking

* Tracks detected objects across video frames
* Maintains object identities during movement
* Provides tracking information for downstream analytics

### 📊 Analytics

The backend includes a dedicated analytics layer for processing surveillance data and generating useful insights from detected and tracked objects.

### ⚡ Real-Time Communication

WebSocket support enables the system to communicate real-time surveillance information between the backend and frontend.

### 🔐 Authentication

The backend includes authentication-related modules and middleware for protecting application resources.

### 🗄️ Database Integration

The system contains dedicated database, repository, and schema layers for persistent application data.

### 🌐 REST API

The backend exposes API routes through **FastAPI** for communication between the frontend and backend.

### 🧪 Testing

The backend includes tests covering important parts of the application, including:

* Database functionality
* Detection
* Video processing
* Tracking

### 🐳 Docker Support

The backend includes a Dockerfile for containerized deployment.

---

## 🛠️ Tech Stack

### Backend

* **Python**
* **FastAPI**
* **OpenCV**
* **YOLO / Ultralytics**
* **SQLAlchemy**
* **Pydantic**
* **WebSockets**
* **JWT Authentication**
* **Alembic**

### Frontend

* **React**
* **Vite**
* **JavaScript**
* Component-based architecture
* API integration
* WebSocket communication

### Database

* **PostgreSQL**

### DevOps

* **Docker**
* Environment-based configuration

---

## 📂 Project Structure

```text
intelligent-video-serveillance-system/
│
├── backend/
│   │
│   ├── app/
│   │   ├── analytics/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── auth/
│   │   ├── core/
│   │   ├── database/
│   │   ├── detection/
│   │   ├── events/
│   │   ├── exceptions/
│   │   ├── middleware/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── tracking/
│   │   ├── utils/
│   │   ├── videos/
│   │   ├── websocket/
│   │   └── main.py
│   │
│   ├── images/
│   ├── Dockerfile
│   ├── create_tables.py
│   ├── testTrack.py
│   ├── test_db.py
│   ├── test_detection.py
│   ├── test_video.py
│   └── requirements.txt
│
├── frontend/
│   │
│   ├── src/
│   │   ├── api/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── routes/
│   │   ├── theme/
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── requirements.txt
└── README.md
```

The repository currently follows this backend/frontend separation and includes dedicated modules for detection, tracking, analytics, authentication, databases, services, videos, and WebSockets.

---

## 🔄 Application Flow

```text
Video Input
     │
     ▼
Frame Extraction
     │
     ▼
Object Detection
     │
     ▼
Object Tracking
     │
     ▼
Event / Analytics Processing
     │
     ├──────────────► Database
     │
     └──────────────► WebSocket
                            │
                            ▼
                     React Dashboard
```

---

## ⚙️ Configuration

The application uses environment-based configuration for runtime settings such as:

```env
DATABASE_URL=your_database_url
VIDEO_SOURCE=0
YOLO_MODEL=yolo_model
CONFIDENCE_THRESHOLD=0.5
PROCESSING_FPS=10
CROWD_THRESHOLD=5
JWT_SECRET_KEY=your_secret_key
```

> Never commit real credentials, API keys, passwords, or production secrets to GitHub.

---

## 🏃 Running the Project

### 1. Clone the repository

```bash
git clone https://github.com/Prathmeshmurkute2/intelligent-video-serveillance-system.git

cd intelligent-video-serveillance-system
```

### 2. Backend

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the FastAPI application:

```bash
uvicorn app.main:app --reload
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend can then communicate with the FastAPI backend through the configured API endpoints.

---

## 🧪 Running Tests

Backend tests are included for different components of the system.

```bash
pytest
```

Individual tests can also be executed during development.

---

## 📌 Current Development Status

**Status: Active Development**

The project already contains the major building blocks of a full-stack intelligent surveillance platform, including:

* AI detection
* Object tracking
* Analytics
* Authentication
* Database layer
* REST APIs
* WebSockets
* React frontend
* Backend tests
* Docker support

The repository currently contains **29 commits** and has separate `backend` and `frontend` applications.

---

## 🔮 Future Improvements

Potential improvements include:

* Multi-camera management
* Advanced alert configuration
* Email/SMS notifications
* Improved analytics dashboards
* Role-based access control
* Event history and filtering
* Model performance optimization
* GPU-accelerated inference
* Cloud deployment
* Production monitoring and logging
* Automated CI/CD pipeline

---

## 🎯 Learning & Engineering Goals

This project was built to gain practical experience with:

* Computer Vision
* AI inference pipelines
* Backend API design
* REST APIs
* WebSockets
* Database architecture
* Authentication
* Frontend/backend integration
* Object tracking
* Testing
* Docker and deployment concepts

The project also demonstrates how an AI/ML component can be integrated into a **production-style full-stack application** rather than being used as an isolated machine-learning script.

---

## 👨‍💻 Author

**Prathmesh Murkute**

GitHub:
https://github.com/Prathmeshmurkute2

---

## ⭐ Project

If you find this project useful or interesting, consider giving the repository a ⭐.
