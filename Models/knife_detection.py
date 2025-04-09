import cv2
import requests
import pyttsx3
import time

API_URL = "http://192.168.160.40:5000/detect"

def text_to_speech():
    engine = pyttsx3.init()
    engine.say("Gun detected")
    engine.runAndWait()

def detect_objects_in_realtime():
    video_capture = cv2.VideoCapture(0)
    gun_detected = False

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        _, img_encoded = cv2.imencode('.jpg', frame)
        response = requests.post(API_URL, files={'frame': img_encoded.tobytes()})

        if response.status_code == 200:
            data = response.json()
            if data.get("gun_detected"):
                if not gun_detected:
                    gun_detected = True
                    print("Gun detected!")
                text_to_speech()
            else:
                gun_detected = False
        else:
            print("Error:", response.text)
        
        cv2.imshow("Client Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_objects_in_realtime()
