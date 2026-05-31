from ultralytics import YOLO
import cv2
from collections import defaultdict

# Load model
model = YOLO("yolov8n.pt")

# Video path
video_path = "../data/videos/CAM 3.mp4"

# Open video
cap = cv2.VideoCapture(video_path)

# Virtual line position
LINE_X = 500

# Track previous positions
track_history = defaultdict(list)

# Prevent duplicate events
processed_ids = set()

while cap.isOpened():

    success, frame = cap.read()

    if not success:
        break

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        classes=[0],
        verbose=False
    )

    annotated_frame = results[0].plot()

    # Draw virtual line
    cv2.line(
        annotated_frame,
        (LINE_X, 0),
        (LINE_X, annotated_frame.shape[0]),
        (0, 255, 255),
        2
    )

    if results[0].boxes.id is not None:

        boxes = results[0].boxes.xyxy.cpu().numpy()
        track_ids = results[0].boxes.id.cpu().numpy().astype(int)

        for box, track_id in zip(boxes, track_ids):

            x1, y1, x2, y2 = box

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            track_history[track_id].append(center_x)

            if len(track_history[track_id]) > 2:

                prev_x = track_history[track_id][-2]

                # Outside -> Inside
                if prev_x < LINE_X and center_x >= LINE_X:

                    print(
                        f"ENTRY | Visitor: VIS_{track_id}"
                    )

                # Inside -> Outside
                elif prev_x > LINE_X and center_x <= LINE_X:

                    print(
                        f"EXIT | Visitor: VIS_{track_id}"
                    )

            cv2.circle(
                annotated_frame,
                (center_x, center_y),
                5,
                (0, 0, 255),
                -1
            )

    cv2.imshow(
        "Entry Exit Detection",
        annotated_frame
    )

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()