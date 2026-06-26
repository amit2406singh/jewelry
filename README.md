# AURA HUID Registry - Backend REST API

This is the Flask backend server that manages connection to MongoDB to securely register, search, and update HUID registry data.

## 🛠️ Requirements & Setup

### Prerequisites
1. **Python 3.8+** installed.
2. **MongoDB** service installed and running locally on `mongodb://localhost:27017/` (or set the environment variable `MONGO_URI`).

### 1. Setup Virtual Environment (Recommended)
Navigate to the `backend` directory and create a virtual environment:
```bash
python -m venv venv
```

Activate the virtual environment:
* **Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
* **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

### 2. Install Packages
Install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Run the Backend Server
Start the Flask dev server:
```bash
python app.py
```
The backend server will run on `http://localhost:5000`.

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status |
| `GET` | `/api/jewelry` | Get all registered HUID items |
| `GET` | `/api/jewelry/<huid>` | Get specific HUID item (triggers verification log) |
| `POST` | `/api/jewelry/register` | Register new gold/jewelry |
| `PUT` | `/api/jewelry/<huid>/status` | Update item status (Stolen/Recovered, verification required) |
| `GET` | `/api/stats` | Dashboard counts (Total registered, Stolen, etc.) |
| `GET` | `/api/logs` | Latest system activity logs |
