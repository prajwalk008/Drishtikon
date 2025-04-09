import cv2
import numpy as np
from numpy import ones, vstack
from numpy.linalg import lstsq
import pyttsx3
from threading import Thread
from queue import Queue
from ultralytics import YOLO
import time
import os

# Initialize TTS engine with error handling
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 235)
    engine.setProperty('volume', 1.0)
except Exception as e:
    print(f"TTS Engine initialization error: {e}")
    # Fallback to print instead of speech if TTS fails
    class FallbackEngine:
        def say(self, text): print(f"Speech: {text}")
        def runAndWait(self): pass
    engine = FallbackEngine()

queue = Queue()

# Initialize YOLO model with CPU settings
try:
    model_path = "gpModel.pt"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file '{model_path}' not found")
    
    model = YOLO(model_path)
    # Force CPU usage
    model.to('cpu')
except Exception as e:
    print(f"Model loading error: {e}")
    raise

# Performance optimization settings
PROCESS_EVERY_N_FRAMES = 2  # Process every 3rd frame
DISPLAY_WIDTH = 640  # Reduced from 800 for better CPU performance
DISPLAY_HEIGHT = 480  # Reduced from 600 for better CPU performance

# Rest of the class sizes definition remains the same
class_avg_sizes = {
    "person": {"width_ratio": 2.5},
    "car": {"width_ratio": 0.37},
    "bicycle": {"width_ratio": 2.3},
    "motorcycle": {"width_ratio": 2.4},
    "bus": {"width_ratio": 0.3},
    "traffic light": {"width_ratio": 2.95},
    "stop sign": {"width_ratio": 2.55},
    "bench": {"width_ratio": 1.6},
    "cat": {"width_ratio": 1.9},
    "dog": {"width_ratio": 1.5},
}

def speak_thread(q):
    while True:
        try:
            if not q.empty():
                message = q.get()
                engine.say(message)
                engine.runAndWait()
            else:
                time.sleep(0.1)
        except Exception as e:
            print(f"Speech thread error: {e}")
            time.sleep(0.1)

def edge_detect(img):
    try:
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Use smaller kernel size for better CPU performance
        blurred = cv2.GaussianBlur(img, (3, 3), 0)
        edges = cv2.Canny(blurred, 250, 300)
        return edges
    except Exception as e:
        print(f"Edge detection error: {e}")
        return np.zeros_like(img)

def roi(img, vertices):
    try:
        mask = np.zeros_like(img)
        if len(mask.shape) == 3:
            cv2.fillPoly(mask, [vertices], (255, 255, 255))
        else:
            cv2.fillPoly(mask, [vertices], 255)
        return cv2.bitwise_and(img, mask)
    except Exception as e:
        print(f"ROI error: {e}")
        return img

# Modified process_lanes function with CPU optimization
def process_lanes(frame, lines):
    try:
        if lines is None:
            return frame, "No lanes detected"
        
        # Simplified lane processing for CPU
        left_lines = []
        right_lines = []
        frame_height = frame.shape[0]
        
        for line in lines:
            for x1, y1, x2, y2 in line:
                if x2 - x1 == 0:
                    continue
                
                slope = (y2 - y1) / (x2 - x1)
                
                # More restrictive slope filtering for stability
                if -0.9 < slope < -0.1:
                    left_lines.append(line)
                elif 0.1 < slope < 0.9:
                    right_lines.append(line)
        
        # Draw lanes if detected
        if left_lines and right_lines:
            # Average left and right lines
            left_avg = np.mean(left_lines, axis=0)[0]
            right_avg = np.mean(right_lines, axis=0)[0]
            
            # Draw the averaged lines
            cv2.line(frame, (int(left_avg[0]), int(left_avg[1])),
                    (int(left_avg[2]), int(left_avg[3])), (0, 255, 0), 2)
            cv2.line(frame, (int(right_avg[0]), int(right_avg[1])),
                    (int(right_avg[2]), int(right_avg[3])), (0, 255, 0), 2)
            
            # Simple direction detection
            mid_point = frame.shape[1] // 2
            left_x = (left_avg[0] + left_avg[2]) // 2
            right_x = (right_avg[0] + right_avg[2]) // 2
            center_x = (left_x + right_x) // 2
            
            if abs(center_x - mid_point) < 30:
                return frame, "Go Straight"
            elif center_x > mid_point:
                return frame, "Turn Left"
            else:
                return frame, "Turn Right"
        
        return frame, "No clear lanes"
            
    except Exception as e:
        print(f"Lane processing error: {e}")
        return frame, "Lane processing error"

# Rest of the helper functions remain the same
def calculate_distance(box, frame_width):
    try:
        object_width = box.xyxy[0, 2].item() - box.xyxy[0, 0].item()
        label = box.cls[0].item()
        class_name = model.names[int(label)]
        
        if class_name in class_avg_sizes:
            object_width *= class_avg_sizes[class_name]["width_ratio"]
        
        if object_width <= 0:
            return float('inf')
        
        distance = (frame_width * 0.5) / np.tan(np.radians(70 / 2)) / object_width
        return round(distance, 2)
    except Exception as e:
        print(f"Distance calculation error: {e}")
        return float('inf')

def get_position(frame_width, box):
    try:
        center_x = (box[0] + box[2]) // 2
        if center_x < frame_width // 3:
            return "LEFT"
        elif center_x < 2 * (frame_width // 3):
            return "FORWARD"
        else:
            return "RIGHT"
    except Exception as e:
        print(f"Position calculation error: {e}")
        return "UNKNOWN"

def blur_person(image, box):
    try:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        head_height = int((y2 - y1) * 0.15)
        if head_height > 0:
            head_region = image[y1:y1 + head_height, x1:x2]
            # Reduced blur kernel size for CPU
            blurred_head = cv2.GaussianBlur(head_region, (15, 15), 0)
            image[y1:y1 + head_height, x1:x2] = blurred_head
        return image
    except Exception as e:
        print(f"Person blurring error: {e}")
        return image

def main():
    try:
        # Check video file existence
        source = "test_file2.mp4"
        if not os.path.exists(source):
            raise FileNotFoundError(f"Video file '{source}' not found")
        
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise RuntimeError("Failed to open video capture")
        
        # Set reduced resolution for better CPU performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, DISPLAY_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, DISPLAY_HEIGHT)
        
        # Start speech thread
        speech_thread = Thread(target=speak_thread, args=(queue,))
        speech_thread.daemon = True
        speech_thread.start()
        
        last_direction_time = time.time()
        last_object_time = time.time()
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("End of video stream")
                break
            
            frame_count += 1
            # Skip frames for better performance
            if frame_count % PROCESS_EVERY_N_FRAMES != 0:
                cv2.imshow('Integrated Detection System', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue
                
            frame = cv2.resize(frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
            frame_copy = frame.copy()
            
            # Lane Detection
            edges = edge_detect(frame_copy)
            # Adjust ROI vertices for new resolution
            roi_vertices = np.array([[80, 440], [300, 280], [360, 280], [640, 440]], np.int32)
            roi_edges = roi(edges, [roi_vertices])
            lines = cv2.HoughLinesP(roi_edges, 2, np.pi/180, 20, minLineLength=7, maxLineGap=7)
            frame, direction = process_lanes(frame, lines)
            
            # Object Detection
            results = model(frame)  # CPU inference
            result = results[0]
            nearest_object = None
            min_distance = float('inf')
            
            if result.boxes:
                for box in result.boxes:
                    try:
                        label = result.names[box.cls[0].item()]
                        coords = [int(x) for x in box.xyxy[0].tolist()]
                        
                        if label in class_avg_sizes:
                            distance = calculate_distance(box, frame.shape[1])
                            
                            if label == "person":
                                frame = blur_person(frame, box)
                                color = (0, 255, 0)
                            elif label == "car":
                                color = (0, 255, 255)
                            else:
                                color = (255, 0, 0)
                            
                            cv2.rectangle(frame, (coords[0], coords[1]), 
                                        (coords[2], coords[3]), color, 2)
                            cv2.putText(frame, f"{label} - {distance:.1f}m", 
                                    (coords[0], coords[1] - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                            
                            if distance < min_distance:
                                min_distance = distance
                                nearest_object = (label, distance, coords)
                    except Exception as e:
                        print(f"Object processing error: {e}")
                        continue
            
            # Audio feedback management
            current_time = time.time()
            
            if current_time - last_direction_time >= 3:
                if direction not in ["Lane processing error", "No lanes detected"]:
                    queue.put(direction)
                    last_direction_time = current_time
            
            if nearest_object and current_time - last_object_time >= 2:
                if nearest_object[1] <= 5.5:
                    position = get_position(frame.shape[1], nearest_object[2])
                    message = f"{nearest_object[0]} {nearest_object[1]:.1f} meters {position}"
                    queue.put(message)
                    last_object_time = current_time
            
            cv2.putText(frame, direction, (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Integrated Detection System', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
    except Exception as e:
        print(f"Main loop error: {e}")
    finally:
        if 'cap' in locals():
            cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
