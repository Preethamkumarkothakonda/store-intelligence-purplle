from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

video_path = "../data/videos/CAM 3.mp4"

results = model.track(
    source=video_path,
    tracker="bytetrack.yaml",
    show=True,
    persist=True,
    classes=[0]
)