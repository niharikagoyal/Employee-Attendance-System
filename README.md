# 🧠 Face Recognition Attendance System with Liveness Detection

A secure AI-based employee attendance system using face recognition and liveness detection built with FastAPI, face_recognition, and a modern frontend UI. This system ensures a real user is present (anti-spoof) before marking attendance using facial verification.

## 🚀 Features
- ✅ Real-time Face Recognition  
- 🧠 Liveness Detection via facial depth landmarks  
- 🌐 Frontend UI with webcam integration  
- 🔐 Secure API with CORS  
- 🔄 External API integration for employee data  
- 🧾 Logging for activity and errors  
- 💾 Base64 image handling & dynamic redirect on match  

## 📁 Project Structure
project/
├── new.py # Main FastAPI backend
├── static/index.html # Frontend HTML UI
├── face_liveness_attendance.log # Log file
└── README.md # This file

markdown
Copy
Edit

## ⚙️ Tech Stack
**Backend:** Python, FastAPI, face_recognition, OpenCV, Pillow, Requests, Logging  
**Frontend:** HTML, CSS, JavaScript (Webcam API)

## 🧑‍💻 How it Works
1. On startup, employee data is fetched from an external API and facial encodings are created.
2. The frontend accesses the webcam and captures a snapshot.
3. The image is sent to the backend via a POST request.
4. The backend verifies liveness using facial landmarks and matches the face with pre-loaded encodings.
5. If matched, it returns employee info and redirects to the attendance marking URL.

## 📷 Liveness Detection
- Uses vertical difference between `nose_bridge` and `eyes`.
- If the difference is too low → flat image → spoof.
- Prevents photo/mask attacks effectively.

## 🔐 API Endpoints
| Method | Route             | Description                          |
|--------|------------------|--------------------------------------|
| GET    | `/`              | Loads the web interface              |
| POST   | `/api/recognize` | Accepts base64 image and returns result |

## 🛠️ Setup & Run

### Prerequisites
- Python 3.10 or 3.11
- Install dependencies:
pip install fastapi uvicorn numpy pillow opencv-python face_recognition requests

shell
Copy
Edit

### Run the App
uvicorn new:app --reload

pgsql
Copy
Edit
Then open your browser at: [http://localhost:8000](http://localhost:8000)

## 🔐 Security & Logging
All face data is used in-memory only.

No images are stored permanently.

## Logging:

Errors, recognition results, and API issues are logged in face_liveness_attendance.log.

You can review this file for monitoring and debugging.

## 📦 Deployment
You can deploy the app using:

Render (https://render.com)

Railway (https://railway.app)

Heroku (https://heroku.com)

PythonAnywhere (https://www.pythonanywhere.com)

Ensure static files and environment variables are properly configured.

## 🎨 UI Features
Webcam video in a circular frame

Live face match button

Animated success/error messages

Smooth responsive design with blur and gradient

## 👩‍💼 Author
Niharika Goyal
BTech CSE | Data Scientist | Python & ML Developer

## 📄 License
MIT License – Feel free to use and modify this for educational or commercial use

