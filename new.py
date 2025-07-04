# import os
# import cv2
# import numpy as np
# import face_recognition
# import requests
# import base64
# import face_recognition_models
# from io import BytesIO
# from PIL import Image, ImageOps  
# from fastapi import FastAPI
# from fastapi.responses import JSONResponse, FileResponse
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware




# os.environ["FACE_RECOGNITION_MODEL_LOCATION"] = face_recognition_models.__path__[0]

# app = FastAPI(title="Face Recognition Attendance API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# employee_encodings = []
# employee_ids = []
# encrypted_ids = []
# employee_names = []
# employee_keys = []

# EXTERNAL_API_URL = "https://project.pisofterp.com/pipl/restworld/employees"


# class ImageData(BaseModel):
#     image: str  # Base64 string




# def load_employee_data_from_api():
#     global employee_encodings, employee_ids, encrypted_ids, employee_names, employee_keys
#     try:
#         resp = requests.get(EXTERNAL_API_URL)
#         resp.raise_for_status()
#     except Exception as e:
#         print(f"API error: {e}")
#         return False

#     data = resp.json()

#     employee_encodings.clear()
#     employee_ids.clear()
#     encrypted_ids.clear()
#     employee_names.clear()
#     employee_keys.clear()

#     for entry in data:
#         emp_id = entry.get("id")
#         encrypted_id = entry.get("encryptedId")
#         pic_b64 = entry.get("employeePic")
#         emp_name = entry.get("employeeName")
#         emp_key = entry.get("key")

#         if not pic_b64 or emp_id is None:
#             continue

#         try:
#             img_bytes = base64.b64decode(pic_b64)
#             img = Image.open(BytesIO(img_bytes)).convert("RGB")
#             img = ImageOps.exif_transpose(img)  # ✅ Rotate image if needed
#             img_np = np.array(img)
#             enc = face_recognition.face_encodings(img_np)
#             if enc:
#                 employee_encodings.append(enc[0])
#                 employee_ids.append(emp_id)
#                 encrypted_ids.append(encrypted_id)
#                 employee_names.append(emp_name)
#                 employee_keys.append(emp_key)
#         except Exception as e:
#             print(f"Error loading image for ID {emp_id}: {e}")

#     return bool(employee_encodings)

# def is_depth_real(landmarks):
#     try:
#         if "nose_bridge" in landmarks and "left_eye" in landmarks and "right_eye" in landmarks:
#             nose_y = landmarks["nose_bridge"][0][1]
#             left_eye_y = landmarks["left_eye"][0][1]
#             right_eye_y = landmarks["right_eye"][0][1]
#             eye_avg_y = (left_eye_y + right_eye_y) / 2
#             vertical_diff = abs(nose_y - eye_avg_y)
#             if vertical_diff < 5:  # tweak threshold as needed
#                 return False, f"Flat depth detected: nose-eye diff = {vertical_diff:.2f}"
#             return True, "Depth looks real"
#         return False, "Required facial landmarks missing"
#     except Exception as e:
#         return False, f"Depth check failed: {str(e)}"


# @app.on_event("startup")
# def startup_event():
#     load_employee_data_from_api()


# @app.get("/")
# def root():
#     return FileResponse("static/index.html")


# @app.post("/api/recognize")
# async def recognize_face(data: ImageData):
#     try:
#         header, encoded = data.image.split(",", 1)
#         img_bytes = base64.b64decode(encoded)
#         img = Image.open(BytesIO(img_bytes)).convert("RGB")
#         img = ImageOps.exif_transpose(img)
#         img_np = np.array(img)

#         landmarks_list = face_recognition.face_landmarks(img_np)
#         if landmarks_list:
#             real_depth, reason = is_depth_real(landmarks_list[0])
#             if not real_depth:
#                 return JSONResponse({
#                     "match": False,
#                     "liveness": False,
#                     "error": f"Liveness failed: {reason}",
#                     "encryptedId": "001"
#                 })

#         face_encodings = face_recognition.face_encodings(img_np)
#         print("Detected faces:", len(face_encodings))  # Debug print

#         for face_encoding in face_encodings:
#             face_distances = face_recognition.face_distance(employee_encodings, face_encoding)
#             best_match_index = np.argmin(face_distances)
#             if face_distances[best_match_index] < 0.55:
#                 matched_id = employee_ids[best_match_index]
#                 matched_encryptedId = encrypted_ids[best_match_index]
#                 matched_name = employee_names[best_match_index]
#                 matched_key = employee_keys[best_match_index]
#                 return JSONResponse({
#                     "match": True,
#                     "employeeId": matched_id,
#                     "encryptedId": matched_encryptedId,
#                     "employeeName": matched_name,
#                     "employeeKey": matched_key
#                 })

#         return JSONResponse({"match": False, "encryptedId": "001"})
#     except Exception as e:
#         return JSONResponse({"error": str(e), "match": False, "encryptedId": "001"})


import os
import cv2
import numpy as np
import face_recognition
import requests
import base64
import face_recognition_models
import logging
from io import BytesIO
from PIL import Image, ImageOps  
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename="face_liveness_attendance.log", level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger()


os.environ["FACE_RECOGNITION_MODEL_LOCATION"] = face_recognition_models.__path__[0]

app = FastAPI(title="Face Recognition Attendance API with Liveness Check")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

employee_encodings = []
employee_ids = []
encrypted_ids = []
employee_names = []
employee_keys = []

EXTERNAL_API_URL = "https://project.pisofterp.com/pipl/restworld/employees"


class ImageData(BaseModel):
    image: str  # Base64 string


def load_employee_data_from_api():
    global employee_encodings, employee_ids, encrypted_ids, employee_names, employee_keys
    try:
        logger.info("Fetching employee data from external API...")
        resp = requests.get(EXTERNAL_API_URL)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"API error: {e}")
        return False

    data = resp.json()
    logger.info(f"Fetched {len(data)} employee records.")

    employee_encodings.clear()
    employee_ids.clear()
    encrypted_ids.clear()
    employee_names.clear()
    employee_keys.clear()

    for entry in data:
        emp_id = entry.get("id")
        encrypted_id = entry.get("encryptedId")
        pic_b64 = entry.get("employeePic")
        emp_name = entry.get("employeeName")
        emp_key = entry.get("key")

        if not pic_b64 or emp_id is None:
            logger.warning(f"Skipping employee with missing image or ID: {emp_name}")
            continue

        try:
            img_bytes = base64.b64decode(pic_b64)
            img = Image.open(BytesIO(img_bytes)).convert("RGB")
            img = ImageOps.exif_transpose(img)
            img_np = np.array(img)
            enc = face_recognition.face_encodings(img_np)
            if enc:
                employee_encodings.append(enc[0])
                employee_ids.append(emp_id)
                encrypted_ids.append(encrypted_id)
                employee_names.append(emp_name)
                employee_keys.append(emp_key)
        except Exception as e:
            logger.error(f"Error loading image for ID {emp_id}: {e}")

    logger.info(f"Loaded {len(employee_encodings)} encodings.")
    return bool(employee_encodings)


def is_depth_real(landmarks):
    try:
        if "nose_bridge" in landmarks and "left_eye" in landmarks and "right_eye" in landmarks:
            nose_y = landmarks["nose_bridge"][0][1]
            left_eye_y = landmarks["left_eye"][0][1]
            right_eye_y = landmarks["right_eye"][0][1]
            eye_avg_y = (left_eye_y + right_eye_y) / 2
            vertical_diff = abs(nose_y - eye_avg_y)
            if vertical_diff < 5:  # tweak threshold as needed
                return False, f"Flat depth detected: nose-eye diff = {vertical_diff:.2f}"
            return True, "Depth looks real"
        return False, "Required facial landmarks missing"
    except Exception as e:
        logger.exception("Depth check failed.")
        return False, f"Depth check failed: {str(e)}"


@app.on_event("startup")
def startup_event():
    logger.info("Starting API and loading employee data...")
    if load_employee_data_from_api():
        logger.info("Employee data loaded successfully.")
    else:
        logger.warning("Employee data failed to load.")


@app.get("/")
def root():
    logger.info("Root route '/' accessed.")
    return FileResponse("static/index.html")


@app.post("/api/recognize")
async def recognize_face(data: ImageData):
    logger.info("Recognition API called.")
    try:
        header, encoded = data.image.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img = ImageOps.exif_transpose(img)
        img_np = np.array(img)

        landmarks_list = face_recognition.face_landmarks(img_np)
        if landmarks_list:
            real_depth, reason = is_depth_real(landmarks_list[0])
            logger.info(f"Liveness Check: {reason}")
            if not real_depth:
                logger.warning("Liveness failed.")
                return JSONResponse({
                    "match": False,
                    "liveness": False,
                    "error": f"Liveness failed: {reason}",
                    "encryptedId": "001"
                })

        face_encodings = face_recognition.face_encodings(img_np)
        logger.info(f"Detected {len(face_encodings)} face(s) in uploaded image.")

        for face_encoding in face_encodings:
            face_distances = face_recognition.face_distance(employee_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if face_distances[best_match_index] < 0.55:
                matched_id = employee_ids[best_match_index]
                matched_encryptedId = encrypted_ids[best_match_index]
                matched_name = employee_names[best_match_index]
                matched_key = employee_keys[best_match_index]

                logger.info(f"Face matched with {matched_name} (ID: {matched_id})")
                return JSONResponse({
                    "match": True,
                    "employeeId": matched_id,
                    "encryptedId": matched_encryptedId,
                    "employeeName": matched_name,
                    "employeeKey": matched_key
                })

        logger.info("No match found.")
        return JSONResponse({"match": False, "encryptedId": "001"})

    except Exception as e:
        logger.exception(f"Error in recognition API: {e}")
        return JSONResponse({"error": str(e), "match": False, "encryptedId": "001"})


