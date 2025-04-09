import cv2
import requests
import pyttsx3

# Flask server URL (replace with your Flask API IP if remote)
server_url = "http://192.168.160.85:8000/detect"

# Initialize TTS (Text-to-Speech) engine
engine = pyttsx3.init()
engine.setProperty("rate", 180)  # Set speaking speed

# Initialize webcam
cap = cv2.VideoCapture(0)

# Keep track of last announced name to avoid repeating
last_name = None

def speak(text):
    engine.say(text)
    engine.runAndWait()

def send_frame_to_server(frame):
    # Encode frame to JPEG
    _, img_encoded = cv2.imencode(".jpg", frame)
    files = {"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")}
    
    try:
        # Send the frame to the server
        response = requests.post(server_url, files=files)

        if response.status_code == 200:
            return response.json().get("detected_name", "Unknown")
        else:
            print(f"❌ Server Error: {response.status_code}, {response.text}")
            return "Unknown"
    except Exception as e:
        print(f"❌ Error sending frame: {e}")
        return "Unknown"

while True:
    # Capture frame from webcam
    ret, frame = cap.read()
    if not ret:
        print("❌ Error capturing frame")
        break

    # Send frame to the server and get the detected name
    detected_name = send_frame_to_server(frame)

    # Announce the detected person only if they are known and not repeated
    if detected_name != "Unknown" and detected_name != last_name:
        print(f"✅ Known Person Detected: {detected_name}")
        speak(f"{detected_name} is detected.")
        last_name = detected_name

    # Display the video feed
    cv2.imshow("Client - Face Recognition", frame)

    # Exit loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
