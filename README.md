# 🧠 Dumroo AI

**Dumroo AI** is an **AI-powered student data query system** that lets users interact with academic datasets using **natural language**.

Built with **FastAPI**, **React (Vite)**, and **Docker** • Powered by **Google Gemini AI** • Hosted on **Render**

---

## ✨ Features

- 🤖 **AI Query Understanding** — Uses Google Gemini to interpret natural language and generate intelligent filters
- 📊 **Real-time Statistics** — Instant insights into student data (grades, scores, submissions)
- ⚡ **FastAPI Backend** — Ultra-fast Python backend powered by `uvicorn` and `uv`
- ⚛️ **React Frontend** — Modern, reactive UI built with Vite
- 🐳 **Dockerized Deployment** — Frontend runs through Nginx container
- ☁️ **Deployed on Render** — Fully managed cloud hosting

---

## 📁 Project Structure

```
Dumroo-ai/
│
├── client/              # React (Vite) Frontend
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── src/
│
└── server/              # FastAPI Backend
    ├── main.py
    ├── config.py
    ├── access_control.py
    ├── query_agent.py
    ├── utils.py
    ├── pyproject.toml
    └── .python-version
```

---

## 🚀 Local Setup

### Prerequisites

- **Node.js** 20+ and **npm**
- **Python** 3.13+
- **Docker** (optional, for containerized frontend)

### 🔧 Backend Setup

The backend uses **`uv`** — a modern, ultra-fast Python package and environment manager.

#### 1. Install `uv`

```bash
pip install uv
```

#### 2. Navigate to server directory

```bash
cd server
```

#### 3. Install dependencies

```bash
uv sync
```

#### 4. Start the FastAPI server

```bash
uv run --active uvicorn main:app --host 0.0.0.0 --port 8000
```

✅ Backend runs at **http://localhost:8000**

---

### 💻 Frontend Setup

#### 1. Navigate to client directory

```bash
cd client
```

#### 2. Install dependencies

```bash
npm install --legacy-peer-deps
```

#### 3. Start development server

```bash
npm run dev
```

✅ Frontend runs at **http://localhost:5173**

---

## 🐳 Docker Setup (Frontend)

### Build and run locally

```bash
cd client
docker build -t dumroo-client .
docker run -p 5173:80 dumroo-client
```

✅ Access at **http://localhost:5173**

---

## ☁️ Deployment on Render

### Backend Configuration

| Setting | Value |
|---------|-------|
| **Type** | Web Service |
| **Root Directory** | `server` |
| **Build Command** | `uv sync` |
| **Start Command** | `uv run --active uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Python Version** | 3.13.9 |

### Frontend Configuration

| Setting | Value |
|---------|-------|
| **Type** | Web Service |
| **Root Directory** | `client` |
| **Environment** | Docker |
| **Port** | 80 |
| **Dockerfile Path** | `client/Dockerfile` |

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google Gemini API key | `AIzaSyXXXX` |
| `ENVIRONMENT` | Environment name | `production` |
| `VITE_API_BASE` | Backend API URL (frontend) | `https://dumroo-ai-praveen.onrender.com` |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/query` | Process natural language query on student data |
| `GET` | `/stats` | Fetch dataset statistics by grade/class |
| `GET` | `/health` | Health check endpoint |

---

## 💡 Example Queries

| Query | Behavior |
|-------|----------|
| *"Who is topper from 7th class?"* | Returns top scorer(s) in grade 7 |
| *"Students who didn't submit homework"* | Filters `homework_submitted == 'No'` |
| *"Topper of section A"* | Finds topper in class A |
| *"Average quiz score per grade"* | Aggregates by grade |
| *"Who got highest marks in the entire school?"* | Finds global highest score |

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React (Vite), Tailwind CSS, ShadCN UI, Framer Motion |
| **Backend** | FastAPI, Pydantic, Pandas, NumPy |
| **AI Engine** | Google Gemini Flash |
| **Containerization** | Docker, Nginx |
| **Hosting** | Render Cloud |

---
