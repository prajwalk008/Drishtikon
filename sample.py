import requests
import pyttsx3
#import time  # Import time module for delay

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)  # Adjust speaking speed

# Define API endpoints
API_URL = "http://192.168.160.40:5000"

# Get GPS location from API
location_response = requests.get(f"{API_URL}/get_location")
if location_response.status_code == 200:
    location_data = location_response.json()
    location_text = f"Current GPS Location: {location_data}"
    print("📍", location_text)
   # engine.say(location_text)
else:
    error_text = "Failed to fetch GPS location."
    print("❌", error_text)
    engine.say(error_text)

# Get navigation route
data = {"end": "88.41,22.6514"}  # Destination coordinates
route_response = requests.post(f"{API_URL}/get_route", json=data)

# Store all step instructions in an array
step_instructions = []

if route_response.status_code == 200:
    route_data = route_response.json()
    print("\n🛣 Navigation Route:")

    for step in route_data.get("route", []):
        step_text = f"Take {step['instruction']} after {step['distance']} meters"
        step_instructions.append(step_text)  # Store in array

else:
    error_text = "Failed to get route."
    print("❌", error_text)
    engine.say(error_text)

# Speak and print all instructions with a delay
for instruction in step_instructions:
    print(instruction)
    engine.say(instruction)
    engine.runAndWait()  # Wait until the current instruction is spoken
    #time.sleep(3)  # 3-second delay before the next instruction