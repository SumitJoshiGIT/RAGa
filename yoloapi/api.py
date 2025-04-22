# detector.py
import cv2
import tensorflow as tf
from yolov4.tf import YOLOv4
from fastapi import FastAPI, UploadFile, File
import cv2
import numpy as np
from detector import detect_objects

app = FastAPI()
yolo = YOLOv4(tiny=True)
yolo.classes = "data/classes/coco.names"
yolo.input_size = (416, 416)
yolo.make_model()
yolo.load_weights("checkpoints/yolov4-tiny-416")

def detect_objects(image_np):
    image = cv2.resize(image_np, (416, 416))
    image = image / 255.0
    image = image[np.newaxis, ...].astype(np.float32)
    boxes, scores, classes, valid_detections = yolo.predict(image)
    return boxes, scores, classes, valid_detections

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    content = await file.read()
    nparr = np.frombuffer(content, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    boxes, scores, classes, valid = detect_objects(image)
    return {
        "boxes": boxes.tolist(),
        "scores": scores.tolist(),
        "classes": classes.tolist()
    }

