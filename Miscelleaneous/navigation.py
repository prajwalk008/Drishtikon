from flask import Flask, request, jsonify
import requests
import time
import geopy.distance
import pyttsx3

app = Flask(__name__)

# OpenRouteService (ORS) API Key (Replace with your own)
ORS_API_KEY = "5b3ce3597851110001cf6248faa6e315ad4d45868b2b0c4265517d0d"

# Initialize Text-to-Speech
engine = pyttsx3.init()
engine.setProperty("rate", 200)


# Function to get directions from ORS
def get_directions(start, end):
    url = f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={ORS_API_KEY}&start={start}&end={end}"
    response = requests.get(url).json()
    
    if "features" in response and response["features"]:
        return response["features"][0]["properties"]["segments"][0]["steps"]
    else:
        return {"error": "Failed to fetch route", "details": response}


# Function to get real-time GPS location
def get_current_location():
    try:
        response = requests.get("https://gpssystem.onrender.com/get_location").json()
        if "latitude" in response and "longitude" in response:
            return f"{response['longitude']},{response['latitude']}"  # Longitude, Latitude format
        else:
            return "81.6296,21.2514"  # Fallback location
    except Exception:
        return "81.6296,21.2514"  # Fallback location


# Function to calculate distance between two GPS coordinates
def calculate_distance(coord1, coord2):
    lat1, lon1 = map(float, coord1.split(","))
    lat2, lon2 = map(float, coord2.split(","))

    return geopy.distance.geodesic((lat1, lon1), (lat2, lon2)).meters


# API Route to get directions
@app.route("/get_route", methods=["POST"])
def get_route():
    data = request.get_json()
    start = data.get("start", get_current_location())  # Get current GPS location if start not provided
    end = data["end"]  # Destination must be provided

    steps = get_directions(start, end)

    return jsonify({"route": steps})


# API Route to get real-time GPS location
@app.route("/get_location", methods=["GET"])
def gps_location():
    return jsonify({"location": get_current_location()})


# API Route for real-time navigation (Text-to-Speech)
@app.route("/navigate", methods=["POST"])
def navigate():
    data = request.get_json()
    steps = data["steps"]

    for step in steps:
        instruction = step["instruction"]
        target_distance = step["distance"]
        message = f"{instruction} after {target_distance:.1f} meters"

        engine.say(message)
        engine.runAndWait()
        time.sleep(1)

    return jsonify({"status": "Navigation Started"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
