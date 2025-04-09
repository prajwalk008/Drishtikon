# import cv2
# from ultralytics import YOLO

# def detect_objects_in_realtime():
#     # Load the YOLO model
#     yolo_model = YOLO('./runs/detect/Normal_Compressed/weights/best.pt')
    
#     # Start capturing video from the webcam
#     video_capture = cv2.VideoCapture(0)  # 0 is usually the default camera

#     while True:
#         ret, frame = video_capture.read()
#         if not ret:
#             print("Failed to grab frame")
#             break
        
#         # Perform object detection
#         results = yolo_model(frame)

#         for result in results:
#             classes = result.names
#             cls = result.boxes.cls
#             conf = result.boxes.conf
#             detections = result.boxes.xyxy

#             for pos, detection in enumerate(detections):
#                 if conf[pos] >= 0.5:  # Confidence threshold
#                     xmin, ymin, xmax, ymax = detection
#                     label = f"{classes[int(cls[pos])]} {conf[pos]:.2f}" 
#                     color = (0, int(cls[pos]), 255)
#                     cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color, 2)
#                     cv2.putText(frame, label, (int(xmin), int(ymin) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

#         # Display the resulting frame with detections
#         cv2.imshow("Real-time Object Detection", frame)

#         # Break the loop on 'q' key press
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     # Release the capture and close any OpenCV windows
#     video_capture.release()
#     cv2.destroyAllWindows()

# # Run the real-time object detection function
# detect_objects_in_realtime()

from flask import Flask, request, jsonify
import cv2
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)

# Load YOLO model
yolo_model = YOLO('./runs/detect/Normal_Compressed/weights/best.pt')

@app.route('/detect', methods=['POST'])
def detect_objects():
    try:
        file = request.files['frame'].read()
        npimg = np.frombuffer(file, np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        results = yolo_model(frame)

        gun_detected = False
        for result in results:
            classes = result.names
            cls = result.boxes.cls
            conf = result.boxes.conf
            detections = result.boxes.xyxy

            for pos, detection in enumerate(detections):
                if conf[pos] >= 0.7:
                    label = classes[int(cls[pos])]
                    if label.lower() == "guns":
                        gun_detected = True
                        break

        return jsonify({"gun_detected": gun_detected})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
